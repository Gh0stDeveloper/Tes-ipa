#!/usr/bin/env bash
# Compile a trusted iOS asset catalog without executing scripts from the input ZIP.
set -euo pipefail

if [[ "$#" -ne 3 ]]; then
  echo "Usage: bash scripts/compile_ipa.sh Assets.xcassets input.ipa output.ipa" >&2
  exit 2
fi
ASSETS="$1"
INPUT="$2"
OUTPUT="$3"
[[ -d "$ASSETS" && -f "$INPUT" ]] || { echo "Assets or IPA not found" >&2; exit 1; }

ASSETS="$(cd "$ASSETS" && pwd)"
INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
mkdir -p "$(dirname "$OUTPUT")"
OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd)/$(basename "$OUTPUT")"
command -v xcrun >/dev/null
command -v codesign >/dev/null
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
unzip -q "$INPUT" -d "$WORK/archive"
shopt -s nullglob
apps=("$WORK"/archive/Payload/*.app)
[[ "${#apps[@]}" -eq 1 ]] || { echo "Expected one .app" >&2; exit 1; }
APP="${apps[0]}"

# Remove stale signature; any bundle resource modification invalidates it.
rm -rf "$APP/_CodeSignature" "$APP/embedded.mobileprovision"
xcrun actool --compile "$APP" \
  --platform iphoneos \
  --minimum-deployment-target 16.0 \
  --target-device iphone \
  --target-device ipad \
  --app-icon AppIcon \
  --output-partial-info-plist "$WORK/AssetCatalogInfo.plist" \
  "$ASSETS"

[[ -s "$APP/Assets.car" ]] || { echo "actool did not produce Assets.car" >&2; exit 1; }
python3 - "$APP/Info.plist" "$WORK/AssetCatalogInfo.plist" <<'PY'
import plistlib, sys
info_path, partial_path = sys.argv[1:]
with open(info_path, 'rb') as f:
    info = plistlib.load(f)
with open(partial_path, 'rb') as f:
    partial = plistlib.load(f)
for key in ('CFBundleIcons', 'CFBundleIcons~ipad'):
    if key in partial:
        info[key] = partial[key]
    else:
        icons = info.setdefault(key, {})
        icons['CFBundlePrimaryIcon'] = {'CFBundleIconName':'AppIcon'}
info['CFBundleDisplayName'] = 'S4NTOS INJECTOR'
info['CFBundleName'] = 'S4NTOS INJECTOR'
info['UILaunchScreen'] = {
    'UIImageName': 'S4NTOSLaunch',
    'UIColorName': 'S4NTOSBackground',
    'UIImageRespectsSafeAreaInsets': False,
}
with open(info_path, 'wb') as f:
    plistlib.dump(info, f, fmt=plistlib.FMT_BINARY)
PY

(cd "$WORK/archive" && zip -qry "$OUTPUT" Payload)
unzip -tq "$OUTPUT" >/dev/null
echo "Compiled unsigned IPA: $OUTPUT"
