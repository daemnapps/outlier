#!/bin/sh
# Put the player and one world on the site.
#   tools/05-portal/engine/publish.sh barbershop
# Copies the three engine files and the world into docs/portal/, writes a
# frames.js from the world's frames.json (hosted copies the player falls
# back to until the frames are in docs/media/portal/<world>/), and rebuilds
# the downloadable kit. Nothing else on the site is touched.
set -eu
world="${1:-barbershop}"
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
src="$root/tools/05-portal/worlds/$world"
out="$root/docs/portal"
test -f "$src/world.js" || { echo "no world at $src"; exit 1; }
mkdir -p "$out"
cp "$here/portal.css" "$here/portal.js" "$out/"
cp "$src/world.js" "$out/world.js"
if [ -f "$src/frames.json" ]; then
  { printf '// hosted copies of the frames, used only when docs/media/portal/%s/<file> is missing\nwindow.PORTAL_IMAGES = ' "$world"; cat "$src/frames.json"; printf ';\n'; } > "$out/frames.js"
else
  printf 'window.PORTAL_IMAGES = {};\n' > "$out/frames.js"
fi
sed -e "s#<script src=\"../worlds/barbershop/world.js\"></script>#<script>window.PORTAL_BASE = '../media/portal/$world/';</script>\n<script src=\"frames.js\"></script>\n<script src=\"world.js\"></script>#" \
    -e 's#<title>Portal</title>#<title>The Shop — a portal</title>#' \
    -e 's#<meta name="robots" content="noindex">##' \
    "$here/index.html" > "$out/index.html"
# the kit people download
( cd "$root/tools" && python3 - <<'PY'
import zipfile, os
z = zipfile.ZipFile('../docs/downloads/portal-kit.zip', 'w', zipfile.ZIP_DEFLATED)
for d, _, fs in os.walk('05-portal'):
    for f in fs:
        if f.endswith('.sh'): continue
        z.write(os.path.join(d, f))
z.close()
PY
)
echo "published $world -> docs/portal/ and docs/downloads/portal-kit.zip"
