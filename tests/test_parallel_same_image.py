"""Quick test: can we generate 2 videos from the same image simultaneously?"""

import asyncio
from grok_web import get_client

TEST_POST = "9ac51419-65c8-467c-958e-97e9f1abadfa"
BASE_PORT = 9222  # Each worker gets BASE_PORT + worker_id


async def create_video_with_own_browser(worker_id: int, post_id: str, command: str):
    """Create a video using its own browser instance on unique port."""
    port = BASE_PORT + worker_id  # Worker 1 → 9223, Worker 2 → 9224
    print(f"[Worker {worker_id}] Starting browser on port {port}...", flush=True)
    try:
        async with get_client(browser_port=port) as client:
            print(f"[Worker {worker_id}] Browser ready, creating video: {command}", flush=True)
            result = await client.create_video(post_id, adjustment_prompt=command)
            if result.moderated:
                print(f"[Worker {worker_id}] ⚠️ Moderated", flush=True)
                return {"worker": worker_id, "command": command, "status": "moderated"}
            else:
                print(f"[Worker {worker_id}] ✅ Success: {result.video_id}", flush=True)
                return {"worker": worker_id, "command": command, "status": "success", "video_id": result.video_id}
    except Exception as e:
        import traceback
        print(f"[Worker {worker_id}] ❌ Error: {e}", flush=True)
        traceback.print_exc()
        return {"worker": worker_id, "command": command, "status": "error", "error": str(e)}


async def main():
    print("Testing parallel video generation on SAME image...")
    print(f"Post: {TEST_POST}")
    print("Each worker gets its own Chrome instance")
    print("=" * 60)

    # Use two different commands to distinguish the results
    commands = ["Zoom In", "Zoom Out"]

    # Launch both requests simultaneously - each with its own browser
    tasks = [
        create_video_with_own_browser(i + 1, TEST_POST, cmd)
        for i, cmd in enumerate(commands)
    ]

    print(f"\nLaunching {len(tasks)} parallel requests (2 Chrome instances)...")
    results = await asyncio.gather(*tasks)

    print("\n" + "=" * 60)
    print("RESULTS:")
    for r in results:
        print(f"  Worker {r['worker']} ({r['command']}): {r['status']}")
        if r.get('video_id'):
            print(f"    → https://grok.com/imagine/post/{r['video_id']}")

    # Check if both succeeded
    successes = [r for r in results if r['status'] == 'success']
    if len(successes) == 2:
        print("\n✅ CONCLUSION: Same image CAN generate 2 videos in parallel!")
    elif len(successes) == 1:
        print("\n⚠️ CONCLUSION: Only 1 succeeded - might be rate limited or just moderation")
    else:
        print("\n❓ CONCLUSION: Both failed - need to retry to determine cause")


if __name__ == "__main__":
    asyncio.run(main())
