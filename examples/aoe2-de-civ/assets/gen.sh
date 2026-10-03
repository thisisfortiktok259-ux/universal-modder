#!/usr/bin/env bash
# The original San Franciscans art came from fal; its true attribution remains.
# This fork makes no asset API calls. For missing 2D art it writes briefs for the Codex
# chat. Generate and import those PNGs before rendering. Models must already be local GLB.
#
#   assets/gen.sh concepts     # missing unit concept briefs
#   assets/gen.sh meshes       # check local robotaxi.glb / drone.glb exist
#   assets/gen.sh images       # missing wonder, emblem, portrait briefs
#   assets/gen.sh all
#
# After replacing a model, check the preview sheet and tune render.forward_yaw / length.
set -euo pipefail
cd "$(dirname "$0")"
UM=${UM:-$(command -v um || echo ../../../bin/um)}
OUT=gen

brief() {  # name composition prompt
  if [ -f "$OUT/$1.png" ] || [ -f "$OUT/$1.jpg" ] || [ -f "$OUT/$1.request.json" ]; then
    return 0
  fi
  "$UM" assets request "$3. Composition: $2." --kind image --opaque --out "$OUT" --name "$1"
}

CONCEPT_STYLE="clean studio product render, three-quarter front view from slightly above, soft even lighting, whole object in frame, isolated on a plain white background, no text, no logos"
# 2D art: the wonder is a single frame, so it can be painted directly in AoE2's projection
AOE_STYLE="in the style of Age of Empires II Definitive Edition building sprites: detailed pre-rendered 3D, warm sunlight from the upper left, isometric three-quarter view from above at 30 degrees, on a plain white background, no text"

concepts() {
  brief robotaxi_concept square_hd "a white compact electric SUV robotaxi, a black spinning lidar sensor dome on the roof, small black sensor pods on the front fenders and mirrors, tinted windows, bright saturated blue accent stripes along the sides and blue wheel rims. $CONCEPT_STYLE"
  brief drone_concept square_hd "a white quadcopter delivery drone with four rotors on arms, carrying a small brown cardboard parcel underneath, bright saturated blue accent panels on the body and the rotor guards. $CONCEPT_STYLE"
}

meshes() {
  for name in robotaxi drone; do
    if [ ! -f "$OUT/$name.glb" ]; then
      echo "Missing $OUT/$name.glb. Supply a licensed or locally authored GLB; chat imagegen does not generate 3D." >&2
      return 2
    fi
  done
}

images() {
  brief wonder portrait_4_3 "the Transamerica Pyramid skyscraper in San Francisco as a game wonder building: a tall white four-sided pyramid tower with narrow vertical windows and two wings near the top, standing on a square grey stone plaza with small palm trees and bright blue banners at the corners, $AOE_STYLE"
  brief emblem square_hd "a heraldic civilization emblem for a game: the Golden Gate Bridge's red-orange tower over blue bay waves on a round golden-bordered shield, flat painted game icon, centered, plain white background, no text"
  brief icon_robotaxi square_hd "a square game unit portrait icon in the painted style of Age of Empires II: a modern white electric self-driving robotaxi crossover with a black lidar sensor dome on its roof and blue trim, three-quarter front view, parked on a medieval cobblestone street between timber houses, dramatic warm lighting, detailed oil painting, no text, no logos"
  brief icon_drone square_hd "a square game unit portrait icon in the painted style of Age of Empires II: a white quadcopter delivery drone carrying a parcel over a medieval town at dusk, dramatic lighting, detailed painting, no text"
}

case "${1:-}" in
  concepts) concepts ;;
  meshes) meshes ;;
  images) images ;;
  all) concepts; meshes; images ;;
  *) sed -n '2,8p' "$0"; exit 1 ;;
esac
