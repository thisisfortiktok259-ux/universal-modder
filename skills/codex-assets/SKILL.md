---
name: codex-assets
description: Create or edit 2D art for a game mod with Codex's native chat image generation when it is available. Use for sprites, icons, concept art and texture images, then import the PNG and prepare engine-ready frames with the local CLI. Does not generate 3D models, audio or video.
---

# 2D assets with Codex

Use the native image generation tool in the current Codex conversation to create or edit an image. It runs in the chat, not in `um` or a standalone shell. Do not claim that `um assets` calls an image model, or ask for a fal or OpenAI API key for this workflow. If the native tool is unavailable in this session, explain that limit and use a user-provided or locally made image.

When `image_gen.imagegen` is available, use its `prompt` and `transparent_background` arguments. For edits, inspect the reference first and pass `referenced_image_paths` for local files; for conversation images without a path use `num_last_images_to_include` instead. Do not pass both reference mechanisms. If the tool returns a local artifact, use that file; if it returns encoded image data, export the actual returned bytes to a PNG. Never replace an unavailable image with a mock or claim a request JSON is generated art. `um assets request` prints compatible tool arguments for local references. Read the installed imagegen skill when needed for tool-specific requirements.

## Make an image

1. Inspect the target game's asset size, palette, outline, perspective and facing. Work only with assets the user may use; do not commit extracted game art.
2. Request a PNG from the native image tool. For a sprite or icon, ask for one isolated object, the required orientation and a transparent background. For concept art or a full background, request an opaque image. For variants or animation frames, edit the base image as a reference and check alignment frame by frame.
3. When a repeatable brief helps, run `um assets request "<subject, style, view>" --out assets/gen --name item --kind sprite` first. Other kinds are `image`, `texture` and `edit`; `--ref base.png` records a reference for an edit and `--opaque` requests an opaque result. This writes a local request JSON; it does not generate an image. Direct generation in the chat does not require a request file.
4. Save the generated PNG locally. If you created a request, run `um assets import generated.png --request <request.json>` to copy it into the output folder and record the manifest. Supply `--model <actual-known-name>` only when the model's name is known; do not guess it.
5. Inspect the image and use `um sprite` to cut out, fit, pixelate, palette-match or pack it into frames. The `asset-pipeline` skill covers those steps. Verify the result in the game.

Imports preserve PNG bytes and append `assets_manifest.jsonl` with prompt, reference hashes, output hash and dimensions. This records caller-supplied provenance; it does not certify which tool generated a file. Credit the actual image tool in the mod's README.

For a reusable character, make a clear base image before requesting edits. Independent generations may drift in shape or camera angle, so compare each variant with the base. A 2D concept can guide separate modeling in Blender, but this image tool does not create a rigged model. Source 3D, sound and video from the user's own licensed files or appropriate local tools.
