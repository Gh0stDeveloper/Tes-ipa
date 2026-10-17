#!/usr/bin/env bash
# Apple-authorized IPA signing using a p12 identity and provisioning profile.
# Requires macOS. Secrets must be provided via GitHub Actions Secrets, never committed.
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: bash scripts/sign_ipa.sh input-compiled.ipa output-signed.ipa" >&2
  exit 2
fi
INPUT="$1"
OUTPUT="$2"
: "${IOS_P12_BASE64:?Missing IOS_P12_BASE64 secret}"
: "${IOS_P12_PASSWORD:?Missing IOS_P12_PASSWORD secret}"
: "${IOS_PROFILE_BASE64:?Missing IOS_PROFILE_BASE64 secret}"
[[ -f "$INPUT" ]] || { echo "Input IPA missing" >&2; exit 1; }
INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
mkdir -p "$(dirname "$OUTPUT")"
OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd)/$(basename "$OUTPUT")"

WORK="$(mktemp -d)"
KEYCHAIN="$WORK/santos.keychain-db"
KEYCHAIN_PASSWORD="$(python3 -c 'import secrets;print(secrets.token_urlsafe(32))')"
cleanup() {
  security delete-keychain "$KEYCHAIN" >/dev/null 2>&1 || true
  rm -rf "$WORK"
}
trap cleanup EXIT

printf '%s' "$IOS_P12_BASE64" | base64 -D > "$WORK/identity.p12"
printf '%s' "$IOS_PROFILE_BASE64" | base64 -D > "$WORK/profile.mobileprovision"
security cms -D -i "$WORK/profile.mobileprovision" > "$WORK/profile.plist"

security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN" >/dev/null
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN"
security set-keychain-settings -lut 21600 "$KEYCHAIN"
security import "$WORK/identity.p12" -k "$KEYCHAIN" -P "$IOS_P12_PASSWORD" -T /usr/bin/codesign >/dev/null
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN" >/dev/null
IDENTITY="$(security find-identity -v -p codesigning "$KEYCHAIN" | grep -Eo '[[:xdigit:]]{40}' | head -n 1 || true)"
[[ -n "$IDENTITY" ]] || { echo "No valid Apple Code Signing identity in p12" >&2; exit 1; }

unzip -q "$INPUT" -d "$WORK/archive"
shopt -s nullglob
apps=("$WORK"/archive/Payload/*.app)
[[ "${#apps[@]}" -eq 1 ]] || { echo "Expected exactly one .app" >&2; exit 1; }
APP="${apps[0]}"

python3 - "$WORK/profile.plist" "$APP/Info.plist" "$WORK/entitlements.plist" "$WORK/profile-certs.txt" "$IDENTITY" <<'PY'
import datetime, hashlib, os, plistlib, sys
prof_path, info_path, ent_path, cert_path, identity = sys.argv[1:]
with open(prof_path, 'rb') as f:
    profile = plistlib.load(f)
with open(info_path, 'rb') as f:
    info = plistlib.load(f)
expires = profile['ExpirationDate'].replace(tzinfo=datetime.timezone.utc)
if expires <= datetime.datetime.now(datetime.timezone.utc):
    raise SystemExit('Apple provisioning profile has expired')
if not profile.get('ProvisionedDevices') and not profile.get('ProvisionsAllDevices'):
    raise SystemExit('This profile appears to be App Store distribution, not device-installable Ad Hoc/development/enterprise')
team = profile['TeamIdentifier'][0]
pattern = profile['Entitlements']['application-identifier']
prefix = team + '.'
if not pattern.startswith(prefix):
    raise SystemExit('Provisioning App ID does not match TeamIdentifier')
allowed = pattern[len(prefix):]
requested = os.environ.get('IOS_BUNDLE_ID', '').strip()
if allowed.endswith('.*'):
    if not requested:
        raise SystemExit('Wildcard provisioning profile requires IOS_BUNDLE_ID secret')
    if not requested.startswith(allowed[:-1]):
        raise SystemExit('IOS_BUNDLE_ID not permitted by provisioning profile')
    bundle_id = requested
else:
    bundle_id = allowed
    if requested and requested != allowed:
        raise SystemExit('IOS_BUNDLE_ID must match the explicit App ID in the profile')
if not bundle_id or '*' in bundle_id or not all(
    c.isalnum() or c in '.-' for c in bundle_id
):
    raise SystemExit('Invalid CFBundleIdentifier')
original = info.get('CFBundleIdentifier','')
info['CFBundleIdentifier'] = bundle_id
with open(info_path, 'wb') as f:
    plistlib.dump(info, f, fmt=plistlib.FMT_BINARY)

source = profile['Entitlements']
ent = {
    'application-identifier': team + '.' + bundle_id,
    'com.apple.developer.team-identifier': team,
}
if 'get-task-allow' in source:
    ent['get-task-allow'] = source['get-task-allow']
if 'keychain-access-groups' in source:
    groups = []
    for group in source['keychain-access-groups']:
        if group.endswith('.*'):
            groups.append(group[:-1] + bundle_id)
        else:
            groups.append(group)
    ent['keychain-access-groups'] = groups
with open(ent_path, 'wb') as f:
    plistlib.dump(ent, f, fmt=plistlib.FMT_XML)
certs = {hashlib.sha1(bytes(cert)).hexdigest().upper() for cert in profile.get('DeveloperCertificates',[])}
with open(cert_path, 'w') as f:
    f.write('\n'.join(sorted(certs)))
if identity.upper() not in certs:
    raise SystemExit('Signing certificate is not included in provisioning profile')
print('Provisioning profile valid; app ID:', bundle_id)
if original != bundle_id:
    print('Bundle ID changed from', original, 'to', bundle_id,
          '(internal hard-coded dependencies may be affected)')
print('Registered device count:',len(profile.get('ProvisionedDevices',[])))
PY

cp "$WORK/profile.mobileprovision" "$APP/embedded.mobileprovision"
rm -rf "$APP/_CodeSignature"
codesign --force --sign "$IDENTITY" --keychain "$KEYCHAIN" \
  --entitlements "$WORK/entitlements.plist" --timestamp=none "$APP"
codesign --verify --verbose=2 "$APP"

(cd "$WORK/archive" && zip -qry "$OUTPUT" Payload)
unzip -tq "$OUTPUT" >/dev/null
echo "Apple-signed IPA created: $OUTPUT"
echo "A physical iPhone installation test is still required."
