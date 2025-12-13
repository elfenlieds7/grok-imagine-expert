"""Test camera commands on Grok Imagine.

Usage:
    python test_camera_commands.py              # Sequential (1 worker)
    python test_camera_commands.py --workers 2  # Parallel (2 Chrome instances)
    python test_camera_commands.py --workers 5 --resume results.json  # Resume from previous run
"""

import argparse
import asyncio
import glob
import json
from datetime import datetime

from grok_web import get_client

# Test configurations
ORBIT_POST = "9ac51419-65c8-467c-958e-97e9f1abadfa"
STATIC_POST = "e396bb74-3204-4eb5-bcec-035d24af9eaa"

BASE_PORT = 9222  # Workers use BASE_PORT + worker_id

# Commands grouped by test post
TESTS = [
    {
        "name": "ORBIT variants",
        "post_id": ORBIT_POST,
        "commands": [
            "Orbit",
            "Orbit 360°",
            "360° clockwise orbit",
            "360° counterclockwise orbit",
            "slow orbit",
            "orbit around subject",
        ],
    },
    {
        "name": "PAN + DISTANCE LOCK",
        "post_id": ORBIT_POST,
        "commands": [
            "Pan Left, locked distance",
            "Pan Left, maintain distance",
            "Pan Right, locked distance",
            "Pan Right, fixed distance from subject",
        ],
    },
    {
        "name": "STATIC variants",
        "post_id": STATIC_POST,
        "commands": [
            "Static Shot",
            "Locked Shot",
            "Locked Off Shot",
            "Immobile Shot",
            "Tripod Shot",
            "Fixed Frame",
            "no camera movement",
            "tripod, no camera shake",
            "stable horizon",
        ],
    },
]

async def test_command(client, post_id: str, command: str, worker_id: int = 0) -> dict:
    """Test a single command, retry until success (unlimited retries)."""
    prefix = f"[W{worker_id}]" if worker_id else ""
    attempt = 0
    while True:
        attempt += 1
        try:
            print(f"{prefix} Attempt {attempt}: {command}...", end=" ", flush=True)
            result = await client.create_video(post_id, adjustment_prompt=command)

            if not result.moderated:
                print(f"✅ video_id={result.video_id}")
                return {
                    "command": command,
                    "post_id": post_id,
                    "video_id": result.video_id,
                    "moderated": False,
                    "attempts": attempt,
                    "url": f"https://grok.com/imagine/post/{result.video_id}",
                }
            else:
                print("⚠️ moderated, retrying...")
        except Exception as e:
            print(f"❌ error: {e}, retrying...")


async def run_sequential():
    """Run all tests sequentially with a single client."""
    results = []

    async with get_client() as client:
        for test_group in TESTS:
            print(f"\n{'='*60}")
            print(f"Testing {test_group['name']} on {test_group['post_id']}")
            print(f"{'='*60}")
            for cmd in test_group["commands"]:
                result = await test_command(client, test_group["post_id"], cmd)
                results.append(result)

    return results


async def worker_task(worker_id: int, commands_queue: asyncio.Queue, results: list):
    """Worker that processes commands from a queue using its own Chrome instance."""
    port = BASE_PORT + worker_id
    print(f"[W{worker_id}] Starting on port {port}...", flush=True)

    async with get_client(browser_port=port) as client:
        print(f"[W{worker_id}] Browser ready", flush=True)
        while True:
            try:
                # Get next command from queue (non-blocking with timeout)
                post_id, command = await asyncio.wait_for(commands_queue.get(), timeout=1.0)
            except TimeoutError:
                # Check if queue is empty and no more items expected
                if commands_queue.empty():
                    break
                continue

            result = await test_command(client, post_id, command, worker_id)
            results.append(result)
            commands_queue.task_done()

    print(f"[W{worker_id}] Done", flush=True)


async def run_parallel(num_workers: int):
    """Run tests in parallel using multiple Chrome instances."""
    results = []
    commands_queue: asyncio.Queue = asyncio.Queue()

    # Flatten all commands into the queue
    for test_group in TESTS:
        print(f"\n{'='*60}")
        print(f"Queuing {test_group['name']} ({len(test_group['commands'])} commands)")
        print(f"{'='*60}")
        for cmd in test_group["commands"]:
            await commands_queue.put((test_group["post_id"], cmd))

    total_commands = commands_queue.qsize()
    print(f"\nTotal commands: {total_commands}")
    print(f"Workers: {num_workers}")
    print(f"Estimated time: ~{total_commands // num_workers} rounds per worker")
    print("=" * 60)

    # Start workers
    workers = [
        asyncio.create_task(worker_task(i + 1, commands_queue, results))
        for i in range(num_workers)
    ]

    # Wait for all commands to be processed
    await commands_queue.join()

    # Cancel workers (they should exit on their own, but just in case)
    for worker in workers:
        worker.cancel()

    # Wait for workers to finish
    await asyncio.gather(*workers, return_exceptions=True)

    return results


def load_previous_results(resume_path: str | None) -> dict[str, dict]:
    """Load previous results and return dict of command -> result for successful ones."""
    successful = {}

    if resume_path:
        # Use specified file
        files = [resume_path] if resume_path else []
    else:
        # Auto-find latest results file
        files = sorted(glob.glob("camera_test_results_*.json"), reverse=True)

    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
                for item in data:
                    if item.get("video_id"):  # Successfully completed
                        successful[item["command"]] = item
            if successful:
                print(f"Loaded {len(successful)} successful results from {f}")
                break
        except Exception as e:
            print(f"Warning: Could not load {f}: {e}")

    return successful


async def main(num_workers: int = 1, resume_path: str | None = None):
    print(f"Camera Command Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'Parallel' if num_workers > 1 else 'Sequential'} ({num_workers} worker(s))")

    # Load previous successful results
    previous_results = load_previous_results(resume_path)

    # Filter out already successful commands from TESTS
    if previous_results:
        for test_group in TESTS:
            original_count = len(test_group["commands"])
            test_group["commands"] = [
                cmd for cmd in test_group["commands"]
                if cmd not in previous_results
            ]
            skipped = original_count - len(test_group["commands"])
            if skipped > 0:
                print(f"Skipping {skipped} already successful commands in {test_group['name']}")

    if num_workers > 1:
        results = await run_parallel(num_workers)
    else:
        results = await run_sequential()

    # Merge with previous successful results
    results.extend(previous_results.values())

    # Save results
    output_file = f"camera_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to {output_file}")
    print(f"{'='*60}")

    # Summary
    print("\nSUMMARY:")
    success = [r for r in results if r.get("video_id")]
    failed = [r for r in results if not r.get("video_id")]
    print(f"  ✅ Success: {len(success)}/{len(results)}")
    print(f"  ❌ Failed: {len(failed)}/{len(results)}")

    if success:
        print("\nSuccessful tests:")
        for r in success:
            print(f"  - {r['command']}: {r['url']}")

    if failed:
        print("\nFailed tests:")
        for r in failed:
            reason = r.get("error", "all moderated")
            print(f"  - {r['command']}: {reason}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test camera commands on Grok Imagine")
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers (each uses its own Chrome instance)",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Resume from previous results file (auto-detects latest if not specified)",
    )
    args = parser.parse_args()

    asyncio.run(main(args.workers, args.resume))
