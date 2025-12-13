# Camera Control Prompts for Grok Imagine

When creating videos with Grok Imagine, you can control camera movement using the `adjustment_prompt` parameter.

## Tested Camera Instructions

All commands tested on 2025-12-13 with demo URLs.

| Command | Description | Status | Demo URL |
|---------|-------------|--------|----------|
| `Static Shot` | Fixed camera, no movement | ✅ | [View](https://grok.com/imagine/post/80a95302-9a41-4cf4-8d7b-bc567b6bab86) |
| `Pan Left` | Camera rotates horizontally left | ✅ | [View](https://grok.com/imagine/post/bb8021c3-18d2-4d61-a75b-ed711b7def06) |
| `Pan Right` | Camera rotates horizontally right | ✅ | [View](https://grok.com/imagine/post/e27f5401-2717-4b13-84a8-e3dd471a57e9) |
| `Tilt Up` | Camera rotates vertically up | ✅ | [View](https://grok.com/imagine/post/9b2882a1-1a00-41ed-9585-1d96bd58c30a) |
| `Tilt Down` | Camera rotates vertically down | ⚠️ | 15次未通过moderation |
| `Zoom In` | Lens adjusts to make subject closer | ✅ | [View](https://grok.com/imagine/post/6a49b78e-86a6-4ddc-9d81-c0da1fe66a20) |
| `Zoom Out` | Lens adjusts to make subject farther | ✅ | [View](https://grok.com/imagine/post/0970120c-85b3-41a1-8f9b-6b001c34e802) |
| `Dolly In` | Camera moves forward toward subject | ✅ | [View](https://grok.com/imagine/post/bc22549d-ffab-44ec-8ed9-5860737a580c) |
| `Dolly Out` | Camera moves backward from subject | ✅ | [View](https://grok.com/imagine/post/7d2b79d9-fa92-4f2c-837e-5909788e2083) |
| `Tracking Shot` | Camera follows the subject | ✅ | 手工测试通过 |
| `Crane Shot` | Camera moves vertically on crane | ✅ | [View](https://grok.com/imagine/post/3852278f-47c0-4604-a9f0-d8572c4c3c0c) |
| `Handheld` | Shaky, documentary-style camera | ✅ | [View](https://grok.com/imagine/post/dbb5cc49-9dd4-4e5c-ae05-f411c86a997a) |
| `Orbit` | Camera circles around subject | ✅ | [View](https://grok.com/imagine/post/242a3b93-f705-450a-82d2-db10b4242cf3) |

## Usage with grok-web-connector

```python
from grok_web import get_client

async with get_client(browser_host="127.0.0.1", browser_port=9222) as client:
    # Static camera - no movement (opposite of forced zoom)
    await client.create_video(post_id, adjustment_prompt="Static Shot")

    # Camera movements
    await client.create_video(post_id, adjustment_prompt="Pan Left")
    await client.create_video(post_id, adjustment_prompt="Dolly Out")
    await client.create_video(post_id, adjustment_prompt="Orbit")

    # Combine with scene description
    await client.create_video(post_id, adjustment_prompt="Static Shot, wind in hair")
```

## Notes

- **Moderation**: Videos may be randomly moderated; retry if needed (typically 5-10 attempts)
- **Case**: Both `Static Shot` and `static shot` work
- **Combining prompts**: Camera instructions can be combined with scene descriptions

## Reference

- [@amXFreeze on X](https://x.com/amXFreeze/status/1976992429908557949) - Original documentation of camera controls
