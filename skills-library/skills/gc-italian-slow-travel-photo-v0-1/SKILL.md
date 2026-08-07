---
name: gc-italian-slow-travel-photo-v0-1
description: Edit and recompose user-provided travel photographs into a natural, restrained Italian slow-travel documentary look with soft available light, warm but unsaturated film color, subtle underexposure, layered foreground blur, clear middle or distant subjects, and generous negative space. Use when the user asks to retouch a travel photo, adjust its composition, crop and rebalance it, soften a foreground, preserve a clear background, add a subtle film character, or avoid HDR, commercial filters, plastic skin, excessive sharpening, and obvious AI artifacts.
---

# Italian Slow-Travel Photo Editing

Edit the supplied photograph non-destructively. Preserve the identity, location, believable geometry, and documentary truth of the scene unless the user explicitly requests a change.

## Workflow

1. Inspect the original image before editing.
2. Identify the intended subject, useful environmental context, distracting edges, and available depth layers.
3. Decide whether the request needs only tonal treatment or also crop, perspective, or compositional rebalancing.
4. Translate the request into an image-editing prompt using the rules below.
5. Use the available image-editing tool with the original image as the edit target.
6. Inspect the result for identity preservation, geometry, natural texture, depth, and AI artifacts.
7. Iterate with one focused correction at a time when needed.

When precise visual values or a ready-to-use prompt scaffold are needed, read [references/visual-recipe.md](references/visual-recipe.md).

## Composition

- Allow cropping, horizon correction, and modest reframing when they strengthen the image.
- Preserve a casual travel-record feeling; avoid a perfectly staged commercial composition.
- Prefer natural negative space and slightly off-center subjects over rigid symmetry.
- Use doors, walls, foliage, tables, chairs, curtains, or passersby as plausible framing layers.
- Permit a noticeably soft foreground when it creates depth, but keep the main subject or middle-to-distant scene legible.
- Avoid invented architecture, duplicated objects, warped furniture, implausible blur boundaries, or large changes to the actual location.
- Do not crop important hands, faces, architectural anchors, or travel context without a clear compositional reason.

## Light and Tone

- Preserve available daylight and believable ambient light direction.
- Favor gentle warmth without an orange cast or excessive saturation.
- Keep exposure neutral to slightly underexposed; retain open, readable shadows.
- Roll highlights off softly and preserve window, sky, skin, and pale-wall detail.
- Use moderate-to-low contrast with a soft tonal shoulder rather than flat gray processing.
- Avoid HDR halos, glowing edges, crushed blacks, aggressive clarity, and artificial cinematic lighting.

## Texture and Color

- Preserve skin pores, fabric, stone, wood, foliage, and atmospheric haze.
- Apply only subtle, fine film grain when it supports the source image.
- Keep greens, terracotta, cream, stone, muted blue, and skin tones restrained and believable.
- Do not add heavy presets, teal-orange grading, plastic smoothing, excessive denoising, or oversharpening.
- Do not beautify faces or bodies unless explicitly requested; even then, keep the adjustment minimal and natural.

## Depth and Blur

- Derive blur from plausible lens depth, subject distance, and occlusion.
- Let a nearby foreground element become soft enough to frame the scene without turning into an opaque digital smear.
- Keep middle and distant planes coherent; do not apply a uniform portrait-mode cutout.
- Preserve natural edge transitions around hair, foliage, glass, railings, and furniture.

## Prompt Construction

State:

1. What may change: crop, balance, tonal treatment, foreground softness, or minor distraction cleanup.
2. What must remain: people, identity, location, architecture, meaningful objects, and natural texture.
3. The desired composition and depth hierarchy.
4. The restrained light, color, contrast, and grain treatment.
5. The avoid list: HDR, commercial preset, plastic skin, oversharpening, excessive saturation, fake bokeh, warped geometry, and obvious AI traces.

Never rely on a photographer's name as the sole style instruction. Express the requested look through concrete visual properties.

## Output

Return the edited image and briefly state the principal changes. Mention any requested change that could not be applied reliably rather than pretending it succeeded.
