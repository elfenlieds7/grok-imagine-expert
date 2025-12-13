# Camera Control Prompts for Grok Imagine

When creating videos with Grok Imagine, you can control camera movement using the `adjustment_prompt` parameter.

## Known Regression (December 2025)

**Warning**: As of December 2025, Grok Imagine has a known regression causing unwanted "forced zoom" effects on many camera commands. Several commands that should only rotate or move the camera also include unexpected zoom-in behavior.

**Source**: [Piunikaweb (2025-12-11)](https://piunikaweb.com/2025/12/11/grok-video-generation-forced-zoom-nsfw-update/) - xAI employee is collecting feedback, may be temporary due to new model testing.

## Camera Commands - Tested Behavior (2025-12-13)

| Command | Expected Behavior | Actual Behavior (Dec 2025) | Status |
|---------|-------------------|---------------------------|--------|
| `Static Shot` | Fixed camera, no movement | Sometimes works, sometimes still zooms in | ⚠️ Unreliable |
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

- **Working normally**: Zoom In/Out, Dolly In/Out, Tracking Shot, Crane Shot
- **Unreliable**: Static Shot (sometimes still zooms)
- **Affected by regression**: Pan Left/Right, Tilt Up, Handheld, Orbit (all have unwanted zoom-in)
- **Unknown**: Tilt Down (moderation issues)

### Recommendation

Due to December 2025 regression, **no reliable way to prevent forced zoom** currently. Try `Static Shot` or alternatives below, but results vary.

## Prompt Structure

Based on [Grok Imagine Prompt Guide](https://www.grokimagineai.net/prompt-guide):

**Basic Formula**: `Subject + Motion + Scene + Shot, Style...`

**Camera placement**: After motion, before style

**Example**: `"Woman walks through forest, Pan Left, cinematic lighting"`

**Key points**:
- Select "Unfixed lens" in basic parameters when using camera movement
- Supported camera types: surround, aerial, zoom, pan, follow, handheld
- Negative prompts do NOT work

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

## Fixed Camera Alternatives (Untested)

Commands that may help prevent camera movement. All untested due to December 2025 regression.

| Command | Difference from `Static Shot` | Source |
|---------|------------------------------|--------|
| `Static Shot` | Standard term | @amXFreeze |
| `Locked Shot` | Same meaning, different wording | Community |
| `Locked Off Shot` | Film industry term | [Rough Cut Media](https://roughcut.media/2025/11/03/cinematic-camera-movement-terms-for-ai-video-prompting/) |
| `Immobile Shot` | More explicit about no movement | Rough Cut Media |
| `Tripod Shot` | Implies stability via equipment | Community |
| `Fixed Frame` | Focus on frame not moving | Community |
| `no camera movement` | Direct instruction | Community |
| `tripod, no camera shake` | Combined instruction | Sora 2 guide |
| `stable horizon` | Focus on horizon stability | Sora 2 guide |

## Additional Camera Commands (Untested)

Commands discovered from community guides. Grouped by category.

### Rotation & Orbit

| Command | Description | Difference |
|---------|-------------|------------|
| `Orbit` | Circle around subject | Basic orbit |
| `Orbit 360°` | Full circle around subject | Complete rotation |
| `360° clockwise orbit` | Full circle, direction specified | Direction control |
| `Arc Shot` | Partial curve around subject | Less than full circle |

### Fast Movements

| Command | Description | Difference |
|---------|-------------|------------|
| `Pan Left/Right` | Slow horizontal rotation | Standard speed |
| `Whip Pan` | Very fast horizontal rotation | Creates motion blur |

### Angle & Perspective

| Command | Description | Difference |
|---------|-------------|------------|
| `Low-angle Shot` | Camera looks up at subject | Subject appears powerful |
| `Bird's Eye View` | Camera directly above, looking down | Top-down view |
| `Overhead Drone` | Aerial view, may include movement | Drone-like footage |
| `Dutch Tilt` | Camera tilted on axis | Creates tension/unease |

### Vertical Movement

| Command | Description | Difference |
|---------|-------------|------------|
| `Crane Shot` | Camera rises/lowers smoothly | On crane arm |
| `Crane Up` | Camera rises on crane | Upward only |

### Camera Feel

| Command | Description | Difference |
|---------|-------------|------------|
| `Handheld` | Slight shake, natural feel | Documentary style |
| `Handheld shake` | More pronounced shake | More intense |

### Focus

| Command | Description | Difference |
|---------|-------------|------------|
| `Zoom In/Out` | Lens zoom, position fixed | No physical movement |
| `Dolly In/Out` | Camera moves forward/back | Physical movement |
| `Push In` | = Dolly In | Alternative term |
| `Pull Out` | = Dolly Out | Alternative term |
| `Focus Pull` | Focus shifts between subjects | Depth effect |

### Speed Modifiers

| Command | Description |
|---------|-------------|
| `Slow Motion` | Slowed down footage |
| `slow dolly-in` | Slow forward movement |

## Reference

- [@amXFreeze on X](https://x.com/amXFreeze/status/1976992429908557949) - Original camera controls documentation
- [GitHub: awesome-grok-imagine-prompts](https://github.com/that-cod/awesome-grok-imagine-prompts) - Community prompt collection
- [腾讯新闻: Grok Imagine元提示词](https://news.qq.com/rain/a/20251015A063PH00) - Chinese prompt guide
- [Rough Cut Media](https://roughcut.media/2025/11/03/cinematic-camera-movement-terms-for-ai-video-prompting/) - AI video camera terms
