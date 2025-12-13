# Camera Control Prompts for Grok Imagine

When creating videos with Grok Imagine, you can control camera movement using the `adjustment_prompt` parameter.

## Known Regression (December 2025)

**Warning**: As of December 2025, Grok Imagine has a known regression causing unwanted "forced zoom" effects on many camera commands. Several commands that should only rotate or move the camera also include unexpected zoom-in behavior.

**Source**: [Piunikaweb (2025-12-11)](https://piunikaweb.com/2025/12/11/grok-video-generation-forced-zoom-nsfw-update/) - xAI employee is collecting feedback, may be temporary due to new model testing.

## Camera Commands - Tested Behavior (2025-12-14)

### Manual Tests (2025-12-13)

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

### Automated Tests (2025-12-14)

**96 videos generated, 25 unique commands tested.**

Full results: [camera_test_all_results.json](../tests/camera_test_all_results.json)

#### ORBIT_POST - Movement Commands ([source image](https://grok.com/imagine/post/9ac51419-65c8-467c-958e-97e9f1abadfa))

| Command | Count | Sample Video | Status |
|---------|-------|--------------|--------|
| `Orbit` | 2 | [link](https://grok.com/imagine/post/ed2c4350-1058-4f2b-97bd-177186762903) | ✅ |
| `orbit around subject` | 4 | [link](https://grok.com/imagine/post/f0dd421e-b09a-4665-8990-364e592c6f81) | ✅ |
| `slow orbit` | 1 | [link](https://grok.com/imagine/post/5c099d2f-c408-4cd2-9bc6-3f8dfa306b18) | ✅ |
| `360° clockwise orbit` | 2 | [link](https://grok.com/imagine/post/c8749aa8-812e-433b-b5ac-2508f3a52307) | ⚠️ |
| `360° counterclockwise orbit` | 1 | [link](https://grok.com/imagine/post/b43c936a-d021-4107-bfa8-c7993bb76e3a) | ⚠️ |
| `Pan Left` | 1 | [link](https://grok.com/imagine/post/bb8021c3-18d2-4d61-a75b-ed711b7def06) | ⚠️ |
| `Pan Left, locked distance` | 1 | [link](https://grok.com/imagine/post/8f09efaf-d6ba-4416-9243-9e5c9b3c3e0f) | ✅ |
| `Pan Left, maintain distance` | 2 | [link](https://grok.com/imagine/post/2b3e0988-c017-4c51-a32b-7ba59faa7236) | ✅ |
| `Pan Left, camera stays in place` | 3 | [link](https://grok.com/imagine/post/cf3a0379-3bde-4e0f-a4c1-e6e529ff6777) | ✅ |
| `Pan Left from camera position` | 2 | [link](https://grok.com/imagine/post/d9d6c640-c2d3-4196-a114-d017689c264a) | ✅ |
| `Rotate camera left` | 2 | [link](https://grok.com/imagine/post/a29531be-bb68-42f4-9f44-966ec3ca3405) | ✅ |
| `Pan Right, fixed distance from subject` | 3 | [link](https://grok.com/imagine/post/c9e322a0-680d-4a48-9238-a8e6efd5dfd8) | ⚠️ |
| `Dolly In` | 1 | [link](https://grok.com/imagine/post/bc22549d-ffab-44ec-8ed9-5860737a580c) | ✅ |
| `Dolly Out` | 1 | [link](https://grok.com/imagine/post/7d2b79d9-fa92-4f2c-837e-5909788e2083) | ✅ |
| `Zoom Out` | 1 | [link](https://grok.com/imagine/post/0970120c-85b3-41a1-8f9b-6b001c34e802) | ✅ |
| `Crane Shot` | 1 | [link](https://grok.com/imagine/post/3852278f-47c0-4604-a9f0-d8572c4c3c0c) | ✅ |
| `Handheld` | 1 | [link](https://grok.com/imagine/post/dbb5cc49-9dd4-4e5c-ae05-f411c86a997a) | ⚠️ |
| `static shot` | 1 | [link](https://grok.com/imagine/post/bdfa4204-5734-4234-be45-81e3147cd26c) | ❓ |

#### STATIC_POST - Static Commands ([source image](https://grok.com/imagine/post/e396bb74-3204-4eb5-bcec-035d24af9eaa))

| Command | Count | Sample Video | Status |
|---------|-------|--------------|--------|
| `no camera movement` | 26 | [link](https://grok.com/imagine/post/42608cd7-a6f8-4368-9e58-89bfde604b77) | ❓ |
| `Fixed Frame` | 30 | [link](https://grok.com/imagine/post/cdcf2b3d-0955-4108-b11a-286849721110) | ❓ |
| `Static Shot` | 3 | [link](https://grok.com/imagine/post/0dec7271-3551-4560-91ef-b9ac3c46fb3f) | ❓ |
| `Tripod Shot` | 3 | [link](https://grok.com/imagine/post/2d7cb36e-c945-42b2-8118-fce27615b588) | ❓ |
| `Locked Off Shot` | 2 | [link](https://grok.com/imagine/post/c286cb71-b67b-4f79-8d29-99e1b9ae0d13) | ❓ |
| `Immobile Shot` | 1 | [link](https://grok.com/imagine/post/d2318efa-6182-4a3e-bdbf-d6fac7a1abfd) | ❓ |

**Legend**: ✅ Works as expected | ⚠️ Has issues (zoom/direction) | ❓ Needs review | ❌ Broken

### Key Findings (Dec 2025)

1. **`Orbit` works WITHOUT zoom** - simple `Orbit`, `orbit around subject`, `slow orbit` all work
2. **"locked distance" / "maintain distance" / "camera stays in place" modifiers help** for Pan commands
3. **`Rotate camera left`** - new working alternative to Pan
4. **`Pan Left from camera position`** - successfully generates different behavior
5. **360° orbit variants have zoom issues** - avoid `360°` in command
6. **Static shots need manual review** - many generated but behavior unclear

### Summary

- **Working normally**: Orbit variants (simple), Dolly In/Out, Zoom Out, Crane Shot
- **Works with modifier**: Pan Left/Right with distance modifiers
- **New alternatives**: `Rotate camera left`, `Pan Left from camera position`
- **Needs review**: All static shot variants (56 videos generated)
- **Has issues**: 360° orbits, Handheld, Pan without modifier

### Recommendation

1. For orbit: Use `Orbit` or `orbit around subject` (not `360°` variants)
2. For pan: Use `Pan Left, locked distance` or `Pan Left from camera position`
3. For rotate: Try `Rotate camera left` as alternative
4. For static: Test multiple variants - `no camera movement` and `Fixed Frame` most common

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

## Fixed Camera Alternatives

Commands that may help prevent camera movement. **Testing shows ALL variants still zoom (Dec 2025).**

| Command | Difference from `Static Shot` | Tested | Result |
|---------|------------------------------|--------|--------|
| `Static Shot` | Standard term | ⚠️ | Unreliable |
| `Locked Shot` | Same meaning, different wording | ❌ | Pending |
| `Locked Off Shot` | Film industry term | ✅ | **Broken** - slowly zooms |
| `Immobile Shot` | More explicit about no movement | ❌ | Pending |
| `Tripod Shot` | Implies stability via equipment | ❌ | Pending |
| `Fixed Frame` | Focus on frame not moving | ✅ | **Broken** - pauses then zooms |
| `no camera movement` | Direct instruction | ❌ | Pending |
| `tripod, no camera shake` | Combined instruction | ❌ | Pending |
| `stable horizon` | Focus on horizon stability | ❌ | Pending |

**Conclusion**: No reliable static shot command found yet. All tested variants have forced zoom.

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
