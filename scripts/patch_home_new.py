#!/usr/bin/env python3
"""Suppress package/advertisement feeds in Home and New of the original IPA.

Requires the exact original 2.1 Beta 2 executable with previously approved
S4NTOS contacts; patches ONLY two Swift ARM64 repository feed-policy functions.
Sources, Installed, Files, updater, version and app identifier stay unchanged.
"""
import hashlib
import plistlib
import struct
import sys
import zipfile
from pathlib import Path

BASE = 0x100000000
EXPECTED_SHA = "aee526022d04fc0bd091d50f146f0b336cbd2261e61cbc13fa9602ee6e0617ea"
SWIFT_RELEASE_STUB = 0x10058fc44
EMPTY_ARRAY_GOT = 0x1006bbdb0
APP = "Payload/3105.app/"
FUNCTIONS = {
    "Home": (0x1002e0fe4, (0xd100c3ff, 0xa9014ff4, 0xa9027bfd, 0x910083fd)),
    "New": (0x1002e1068, (0xd10103ff, 0xa90157f6, 0xa9024ff4, 0xa9037bfd)),
}

def branch_to(pc, dest):
    delta = dest - pc
    assert delta % 4 == 0 and -(1 << 27) <= delta < (1 << 27)
    return 0x94000000 | ((delta >> 2) & 0x3ffffff)

def got_page(reg, pc, target):
    delta = (target >> 12) - (pc >> 12)
    assert -(1 << 20) <= delta < (1 << 20)
    imm = delta & 0x1fffff
    return 0x90000000 | ((imm & 3) << 29) | ((imm >> 2) << 5) | reg

def patch_exe(before):
    if hashlib.sha256(before).hexdigest() != EXPECTED_SHA:
        raise ValueError("Refusing binary other than verified original 2.1 Beta 2 + About contacts")
    data = bytearray(before)
    allowed = set()
    for screen, (address, original) in FUNCTIONS.items():
        offset = address - BASE
        assert struct.unpack_from("<4I", data, offset) == original, screen
        # Input x0 is the retained Swift Array storage from RepositoryStore.
        # Release the original array (+1); then return Swift's immortal shared
        # empty-array storage in x0. No stored sources/packages are mutated.
        patch = [
            0xd10043ff,                                   # sub sp,sp,#16
            0xf90003fe,                                   # str x30,[sp]
            branch_to(address + 8, SWIFT_RELEASE_STUB),   # bl swift_release
            got_page(8, address + 12, EMPTY_ARRAY_GOT),   # adrp x8, __swiftEmptyArrayStorage@gotpage
            0xf9400000 | ((0xdb0 // 8) << 10) | (8 << 5),  # ldr x0,[x8,#0xdb0]
            0xf94003fe,                                   # ldr x30,[sp]
            0x910043ff,                                   # add sp,sp,#16
            0xd65f03c0,                                   # ret
        ]
        struct.pack_into("<8I", data, offset, *patch)
        assert struct.unpack_from("<8I", data, offset) == tuple(patch)
        allowed.update(range(offset, offset + 32))
        print(f"{screen}: patched 32 instruction bytes at {offset:#x}")
    changes = {i for i, (a, b) in enumerate(zip(before, data)) if a != b}
    if not changes or not changes.issubset(allowed) or len(data) != len(before):
        raise ValueError("Executable modified outside two Home/New feed-policy functions")
    print(f"Only {len(changes)} executable bytes changed")
    return bytes(data)

def run(src, dst):
    src, dst = Path(src), Path(dst)
    if src.resolve() == dst.resolve():
        raise ValueError("Output must differ from original input")
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None:
            raise ValueError("Source IPA integrity failure")
        files = [(i, z.read(i.filename)) for i in z.infolist() if not i.is_dir()]
    info = plistlib.loads(next(data for i, data in files if i.filename == APP + "Info.plist"))
    for key, value in {
        "CFBundleIdentifier": "com.apple.mobile.MobileHouseArrest",
        "CFBundleShortVersionString": "2.1",
        "CFBundleVersion": "2",
        "AppReleaseDisplayVersion": "2.1 Beta 2",
        "CFBundleExecutable": "3105",
        "CFBundleDisplayName": "S4NTOS INJECTOR",
    }.items():
        if info.get(key) != value:
            raise ValueError(f"Unexpected original IPA metadata {key}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for item, data in files:
            if item.filename == APP + "3105":
                data = patch_exe(data)
            z.writestr(item, data)
    with zipfile.ZipFile(dst) as z:
        assert z.testzip() is None
        assert plistlib.loads(z.read(APP + "Info.plist")) == info
        patched = z.read(APP + "3105")
        for unchanged in (
            b"https://api.github.com/repos/YangJiiii/3105/releases/latest",
            b"https://raw.githubusercontent.com/YangJiiii/3105-repo/main/sources.json",
            b"https://wa.me/573505589046",
            b"https://discord.gg/b6xnTpUK5w",
            b"https://t.me/S4ntosOWNER",
            b"https://tiktok.com/@s4ntosxiter1",
        ):
            assert unchanged in patched, f"Original updater/source/client contact changed: {unchanged}"
    print("PASS: Home/New produce no package listings. All other app details unchanged.")
    print("Note: original empty-state UI may still show an icon or empty-message shell.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: patch_home_new.py input-contacts.ipa output-home-new.ipa")
    run(sys.argv[1], sys.argv[2])
