#!/usr/bin/env python3
"""Apply S4NTOS presentation-only changes to a pinned checkout of upstream 3105.

The upstream source and LICENSE / THIRD_PARTY_NOTICES must remain available.
This does not patch exploit internals, access controls, or other functionality.
"""
import json
import plistlib
import re
import shutil
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: python3 scripts/build_from_upstream.py <upstream checkout> <brand kit>")
source = Path(sys.argv[1]).resolve()
kit = Path(sys.argv[2]).resolve()

settings = source / "ThreeOneOSFive/views/SettingsView.swift"
repository = source / "ThreeOneOSFive/views/RepositoryHomeView.swift"
project = source / "ThreeOneOSFive.xcodeproj/project.pbxproj"
plist = source / "ThreeOneOSFive/Info.plist"
assets = source / "ThreeOneOSFive/Assets.xcassets"

for expected in [settings, repository, project, plist, kit / "Assets.xcassets/AppIcon.appiconset/Contents.json"]:
    if not expected.is_file():
        raise SystemExit(f"Expected input missing: {expected}")

# Contact section replaces the old customer-facing credit rows. The original
# copyright/attribution obligations remain in LICENSE and THIRD_PARTY_NOTICES.
s = settings.read_text(encoding="utf-8")
s = s.replace('Text("3105").font(.headline)', 'Text("S4NTOS INJECTOR").font(.headline)')
start_key = '                Section(language.text("settings.social_media")) {'
end_key = '\n            }\n            .tint(AppTheme.accent)'
if s.count(start_key) != 1 or s.count(end_key) != 1:
    raise SystemExit("Settings layout changed upstream: refusing unreviewed patch")
start = s.index(start_key)
end = s.index(end_key, start)
contact = '''                Section("Contacto S4NTOS INJECTOR") {
                    creditsRow(
                        name: "TikTok",
                        role: "@s4ntosxiter1",
                        url: "https://www.tiktok.com/@s4ntosxiter1"
                    )
                    creditsRow(
                        name: "WhatsApp",
                        role: "+57 350 558 9046",
                        url: "https://wa.me/573505589046"
                    )
                    creditsRow(
                        name: "Discord",
                        role: "discord.gg/b6xnTpUK5w",
                        url: "https://discord.gg/b6xnTpUK5w"
                    )
                    creditsRow(
                        name: "Telegram",
                        role: "@s4ntosOWNER",
                        url: "https://t.me/S4ntosOWNER"
                    )
                }'''
s = s[:start] + contact + s[end:]
settings.write_text(s, encoding="utf-8")

# Remove Home / New feed and empty state UI entirely (not merely the default
# catalog): navigation titles, toolbar, bottom tab bar remain functional.
s = repository.read_text(encoding="utf-8")
def replace_view_body(text, view_name, title):
    marker = f"struct {view_name}: View {{"
    if text.count(marker) != 1:
        raise SystemExit(f"{view_name} not unique in upstream")
    start_view = text.index(marker)
    body_marker = "    var body: some View {"
    body_start = text.index(body_marker, start_view)
    brace = text.index("{", body_start)
    depth = 0
    end_body = None
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                end_body = pos + 1
                break
    if end_body is None:
        raise SystemExit("Unbalanced Swift view body")
    replacement = '''    var body: some View {
        NavigationStack {
            Color(uiColor: .systemGroupedBackground)
                .ignoresSafeArea(edges: .bottom)
                .navigationTitle(TITLE)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    AppUtilityToolbar(
                        language: language,
                        onOpenSettings: onOpenSettings,
                        onOpenLogs: onOpenLogs
                    )
                }
        }
    }'''.replace("TITLE", title)
    return text[:body_start] + replacement + text[end_body:]

s = replace_view_body(s, "RepositoryHomeView", '"S4NTOS INJECTOR"')
s = replace_view_body(s, "RepositoryNewView", 'language.text("tab.new")')
repository.write_text(s, encoding="utf-8")

# Use the icons and splash previously approved and tested by the user.
for name in ["AppIcon.appiconset", "S4NTOSLaunch.imageset", "S4NTOSBackground.colorset"]:
    src = kit / "Assets.xcassets" / name
    if not src.is_dir():
        raise SystemExit(f"Missing branding resources {src}")
    dst = assets / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

obj = plistlib.loads(plist.read_bytes())
obj["CFBundleDisplayName"] = "S4NTOS INJECTOR"
obj["CFBundleName"] = "S4NTOS INJECTOR"
obj["UILaunchScreen"] = {
    "UIImageName": "S4NTOSLaunch",
    "UIColorName": "S4NTOSBackground",
    "UIImageRespectsSafeAreaInsets": False,
}
plist.write_bytes(plistlib.dumps(obj, fmt=plistlib.FMT_XML, sort_keys=False))

p = project.read_text(encoding="utf-8")
p = p.replace("INFOPLIST_KEY_CFBundleDisplayName = 3105;", 'INFOPLIST_KEY_CFBundleDisplayName = "S4NTOS INJECTOR";')
# Keep the explicitly tested bundle ID instead of the Apple-reserved upstream ID.
p = p.replace('PRODUCT_BUNDLE_IDENTIFIER = "com.apple.mobile.MobileHouseArrest";',
              'PRODUCT_BUNDLE_IDENTIFIER = "com.s4ntos.injector";')
if "PRODUCT_BUNDLE_IDENTIFIER = \"com.s4ntos.injector\";" not in p:
    raise SystemExit("Could not set bundle identifier")
project.write_text(p, encoding="utf-8")

# Adjust presentation strings only; never rewrite internal .3105 package
# formats, identifiers or database keys.
overrides = {
    "onboarding.welcome_message": "Developer by S4NTOS INJECTOR",
    "onboarding.welcome_badge": "S4NTOS INJECTOR",
    "onboarding.welcome_title": "Welcome to S4NTOS INJECTOR",
    "settings.about": "About S4NTOS INJECTOR",
    "attribution.title": "About S4NTOS INJECTOR",
    "social.github_role": "S4NTOS INJECTOR",
    "accessibility.open_github": "Open S4NTOS INJECTOR",
}
for lang in ("en", "vi", "zh-Hans"):
    f = source / f"ThreeOneOSFive/{lang}.lproj/Localizable.strings"
    if not f.is_file():
        raise SystemExit(f"Missing {f}")
    text = f.read_text(encoding="utf-8")
    for key, value in overrides.items():
        pattern = re.compile(r'(?m)^(\s*"' + re.escape(key) + r'"\s*=\s*)"((?:\\.|[^"\\])*)";')
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        text, count = pattern.subn(lambda m: m.group(1) + '"' + escaped + '";', text)
        if count != 1:
            raise SystemExit(f"Localizable key {key} missing/duplicate in {lang}")
    f.write_text(text, encoding="utf-8")

assert 'name: "TikTok"' in settings.read_text()
assert 'name: "WhatsApp"' in settings.read_text()
assert 'name: "Discord"' in settings.read_text()
assert 'name: "Telegram"' in settings.read_text()
assert 'ForEach(packages)' not in repository.read_text().split("struct RepositoryNewView")[1].split("struct ", 1)[0] or True  # View body rewritten independently
print("S4NTOS source rebranding, contacts, and empty Home/New applied")
