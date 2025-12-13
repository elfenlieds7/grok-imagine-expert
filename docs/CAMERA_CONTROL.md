# Camera Control Prompts for Grok Imagine

When creating videos with Grok Imagine, you can control camera movement using the `adjustment_prompt` parameter.

## Known Regression (December 2025)

**Warning**: As of December 2025, Grok Imagine has a known regression causing unwanted "forced zoom" effects on many camera commands. Several commands that should only rotate or move the camera also include unexpected zoom-in behavior.

**Source**: [Piunikaweb (2025-12-11)](https://piunikaweb.com/2025/12/11/grok-video-generation-forced-zoom-nsfw-update/) - xAI employee is collecting feedback, may be temporary due to new model testing.

## Camera Commands - Tested Behavior (2025-12-13)

| Command | Expected Behavior | Actual Behavior (Dec 2025) | Status |
|---------|-------------------|---------------------------|--------|
| `Static Shot` | Fixed camera, no movement | No movement at all | ✅ Normal |
| `Pan Left` | Camera rotates horizontally left | Rotates left around subject + zooms in to subject's right side | ⚠️ Regression |
| `Pan Right` | Camera rotates horizontally right | Rotates right around subject + zooms in to subject's left side | ⚠️ Regression |
| `Tilt Up` | Camera rotates vertically up | Zooms in + rises, stops above subject's head (subject exits frame) | ⚠️ Regression |
| `Tilt Down` | Camera rotates vertically down | Failed moderation 15 times | ❓ Unknown |
| `Zoom In` | Lens zooms closer to subject | Slowly zooms in | ✅ Normal |
| `Zoom Out` | Lens zooms away from subject | Slowly zooms out | ✅ Normal |
| `Dolly In` | Camera moves forward toward subject | Slowly moves closer | ✅ Normal |
| `Dolly Out` | Camera moves backward from subject | Slowly moves away | ✅ Normal |
| `Tracking Shot` | Camera follows moving subject | Follows subject, maintains distance | ✅ Normal |
| `Crane Shot` | Camera moves vertically on crane | Rises while staying aimed at subject | ✅ Normal |
| `Handheld` | Shaky, documentary-style movement | Slowly zooms in + slight vertical wobble | ⚠️ Regression |
| `Orbit` | Camera circles around subject | Rotates to upper-right + zooms in, ends up above subject looking down (inverted) | ⚠️ Regression |

### Summary

- **Working normally**: Static Shot, Zoom In/Out, Dolly In/Out, Tracking Shot, Crane Shot
- **Affected by regression**: Pan Left/Right, Tilt Up, Handheld, Orbit (all have unwanted zoom-in)
- **Unknown**: Tilt Down (moderation issues)

### Recommendation

Use `Static Shot` if you want to avoid forced zoom effects until this regression is fixed.

## Usage with grok-web-connector

```python
from grok_web import get_client

# Chrome auto-launches if not running (isolated profile)
async with get_client() as client:
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
