#!/usr/bin/env python3
"""Hotfix the original 2.1 Beta 2 S4NTOS IPA, without recompiling older sources.

Input is the branded 2.1 Beta 2 IPA from the already tested first kit, after
actool compiled its icon and splash. Only original app's update-check URL and
plist identity/version metadata change; no UIKit/SwiftUI views are rewritten.
"""
import argparse
import hashlib
import os
from pathlib import Path
import plistlib
import shutil
import tempfile
import zipfile

ORIGINAL_UPDATE = b"https://api.github.com/repos/YangJiiii/3105/releases/latest"
NO_LEGACY_UPDATES = b"https://api.github.com/repos/YangJiiii/3105/releases/nosync"
assert len(ORIGINAL_UPDATE) == len(NO_LEGACY_UPDATES)
APP = "Payload/3105.app"
BUNDLE_ID = "com.s4ntos.injector"
EXPECTED_ORIGINAL_VERSION = "2.1"
TARGET_VERSION = "2.2.1"
TARGET_BUILD = "2201"
SOURCE_DISPLAY = "2.1 Beta 2"
MARKER = "S4NTOS-ORIGINAL-2.1-BETA2-VERSION-HOTFIX-2201"

def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("input_ipa", type=Path)
    cli.add_argument("output_ipa", type=Path)
    args = cli.parse_args()
    source, target = args.input_ipa.resolve(), args.output_ipa.resolve()
    if source == target:
        raise SystemExit("Input/output cannot be the same")
    with tempfile.TemporaryDirectory(prefix="s4ntos-original-") as folder:
        root = Path(folder)
        with zipfile.ZipFile(source) as zipped:
            members = zipped.infolist()
            # Preserve only a conventional single-app IPA.
            app_roots = {m.filename.split(".app/", 1)[0] + ".app" for m in members
                         if m.filename.startswith("Payload/") and ".app/" in m.filename}
            if app_roots != {APP}:
                raise SystemExit(f"Unexpected IPA app roots: {app_roots}")
            for m in members:
                p = Path(m.filename)
                if p.is_absolute() or ".." in p.parts or m.filename.startswith("/"):
                    raise SystemExit("Unsafe IPA path")
            zipped.extractall(root)
        bundle = root / APP
        info_file = bundle / "Info.plist"
        info = plistlib.loads(info_file.read_bytes())
        if info.get("CFBundleShortVersionString") != EXPECTED_ORIGINAL_VERSION:
            raise SystemExit(f"Refusing non-2.1 IPA: {info.get('CFBundleShortVersionString')}")
        if info.get("AppReleaseDisplayVersion") != SOURCE_DISPLAY:
            raise SystemExit("Refusing IPA that is not original 2.1 Beta 2 build")
        if info.get("CFBundleExecutable") != "3105":
            raise SystemExit("Unexpected executable")
        exe = bundle / "3105"
        before = exe.read_bytes()
        if before.count(ORIGINAL_UPDATE) != 1:
            raise SystemExit("Unexpected update checker: original URL missing/ambiguous")
        after = before.replace(ORIGINAL_UPDATE, NO_LEGACY_UPDATES)
        if len(after) != len(before):
            raise SystemExit("Mach-O length changed")
        assert after.replace(NO_LEGACY_UPDATES, ORIGINAL_UPDATE) == before
        exe.write_bytes(after)
        # ZipFile.extractall does not preserve UNIX executable bits.
        # iOS requires the Mach-O file to be executable after re-signing.
        exe.chmod(0o755)
        # Keep the tested independent app ID. Never change the original
        # com.apple.mobile.* identifier or other private system entitlements.
        if info.get("CFBundleIdentifier") != BUNDLE_ID:
            raise SystemExit(f"Unexpected app ID {info.get('CFBundleIdentifier')}")
        info["CFBundleDisplayName"] = "S4NTOS INJECTOR"
        info["CFBundleName"] = "S4NTOS INJECTOR"
        info["CFBundleShortVersionString"] = TARGET_VERSION
        info["CFBundleVersion"] = TARGET_BUILD
        info["AppReleaseDisplayVersion"] = "2.2.1 · S4NTOS INJECTOR"
        info["S4NTOSBuildMarker"] = MARKER
        info_file.write_bytes(plistlib.dumps(info, fmt=plistlib.FMT_BINARY, sort_keys=False))

        (bundle / "_CodeSignature").is_dir() and shutil.rmtree(bundle / "_CodeSignature")
        (bundle / "embedded.mobileprovision").is_file() and (bundle / "embedded.mobileprovision").unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
            for path in sorted((root / "Payload").rglob("*")):
                if path.is_file():
                    output.write(path, arcname=str(path.relative_to(root)))
        with zipfile.ZipFile(target) as zipped:
            loaded = plistlib.loads(zipped.read(APP + "/Info.plist"))
            final_binary = zipped.read(APP + "/3105")
            if (loaded.get("CFBundleShortVersionString"), loaded.get("CFBundleVersion")) != (TARGET_VERSION, TARGET_BUILD):
                raise SystemExit("Unexpected final version")
            if loaded.get("S4NTOSBuildMarker") != MARKER:
                raise SystemExit("Missing marker")
            if final_binary != after:
                raise SystemExit("Mach-O changed during packaging")
            if zipped.testzip() is not None:
                raise SystemExit("Archive integrity check failed")
        print("Original working app retained: 2.1 Beta 2 executable")
        print("Bumped app package: 2.2.1 (2201), bundle com.s4ntos.injector")
        print("Legacy upstream update check disabled by fixed-length endpoint replacement")
        print("Executable originally:", hashlib.sha256(before).hexdigest())
        print("Executable patched:   ", hashlib.sha256(after).hexdigest())
        print("IPA:", target)

if __name__ == "__main__":
    main()
