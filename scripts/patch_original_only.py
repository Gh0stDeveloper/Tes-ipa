#!/usr/bin/env python3
"""S4NTOS branding-only patch for the verified original iOS 2.1 Beta 2 IPA.

Do NOT change the updater, version, bundle ID, repository feed or iOS logic.
Patch only About's compiled Swift literals, URL constants and translations.
Fails closed if the source executable differs from the user's original upload.
"""
import hashlib, plistlib, struct, sys, zipfile
from pathlib import Path

SHA256="d5b95ed6ce634cb5f8f8734f31e4a83212a3341ad59389706482a796cdfbab7b"
APP="Payload/3105.app/"

# Exact ARM64 MOVZ/MOVK locations for two copies of each About title literal.
# Columns: original, replacement, first 8 bytes path A/B, second 8 bytes A/B.
NAMES=(
("GitHub","TikTok",(0x42754,0x42758,0x4275c),(0x42814,0x42818,0x4281c),(),()),
("YangJiii","WhatsApp",(0x43320,0x43324,0x43328,0x4332c),(0x433e4,0x433e8,0x433ec,0x433f0),(),()),
("0xjohnnydev","Discord",(0x43688,0x4368c,0x43690,0x43694),(0x4375c,0x43760,0x43764,0x43768),(0x43698,0x4369c,0x436a0),(0x43770,0x43774,0x43778)),
("LeminLimez","TikTok",(0x439f0,0x439f4,0x439f8,0x439fc),(0x43ac8,0x43acc,0x43ad0,0x43ad4),(0x43a00,0x43a04),()),
("CrazyMind90","Discord",(0x43d44,0x43d48,0x43d4c,0x43d50),(0x43e18,0x43e1c,0x43e20,0x43e24),(0x43d54,0x43d58,0x43d5c),()),
("forcequitOS","WhatsApp",(0x44090,0x44094,0x44098,0x4409c),(0x44168,0x4416c,0x44170,0x44174),(0x440a0,0x440a4,0x440a8),(0x4417c,0x44180,0x44184)),
)
# Same-byte-length URL changes prevent writing over unrelated Swift constants.
# URL #fragments are ignored by the destination services.
URLS={
5865904:("https://x.com/duongduong0908","https://wa.me/573505589046#x"),
5865968:("https://github.com/0xjohnnydev/FilzaSlop","https://discord.gg/b6xnTpUK5w#"+"x"*10),
5866048:("https://github.com/leminlimez/Pocket-Poster","https://www.tiktok.com/@s4ntosxiter1#"+"x"*6),
5866128:("https://github.com/CrazyMind90","https://t.me/S4ntosOWNER#"+"x"*5),
5866192:("https://github.com/forcequitOS","https://wa.me/573505589046#xxx"),
5866288:("https://github.com/YangJiiii/3105","https://tiktok.com/@s4ntosxiter1#"),
# HTTP redirects to the HTTPS address provided by the client; this 23-byte
# inline URL cannot fit the 24-byte canonical HTTPS Telegram URL.
5866400:("https://t.me/ioscrackvn","http://t.me/S4ntosOWNER"),
}
LABELS={
"social.github_role":"@s4ntosxiter1",
"social.iosvn_role":"@s4ntosOWNER",
"credit.yangjiii":"+57 350 558 9046",
"credit.filzaslop":"discord.gg/b6xnTpUK5w",
"credit.pocket_poster":"@s4ntosxiter1",
"credit.sandbox_escape":"discord.gg/b6xnTpUK5w",
"credit.forcequit":"+57 350 558 9046",
}
EXPECTED={
"CFBundleIdentifier":"com.apple.mobile.MobileHouseArrest",
"CFBundleShortVersionString":"2.1",
"CFBundleVersion":"2",
"AppReleaseDisplayVersion":"2.1 Beta 2",
"CFBundleExecutable":"3105",
}

def change_imm(data,offset,old,new):
    instruction=struct.unpack_from("<I",data,offset)[0]
    hw=(instruction>>21)&3
    if instruction & 0xff800000 not in (0xd2800000,0xf2800000):
        raise ValueError("Unexpected ARM opcode at "+hex(offset))
    if ((instruction>>5)&0xffff)!=old:
        raise ValueError("Unexpected Swift immediate at "+hex(offset))
    instruction=(instruction & ~(0xffff<<5)) | (new<<5)
    struct.pack_into("<I",data,offset,instruction)

def swift_small(text):
    v=text.encode("utf-8")
    if not 0<len(v)<=15: raise ValueError("Not a Swift small string")
    return v+b"\0"*(15-len(v))+bytes([0xe0+len(v)])

def patch_group(data,addresses,old,new):
    for off in addresses:
        instruction=struct.unpack_from("<I",data,off)[0]
        hw=(instruction>>21)&3
        change_imm(data,off,
            int.from_bytes(old[2*hw:2*hw+2],"little"),
            int.from_bytes(new[2*hw:2*hw+2],"little"))

def patch_binary(blob):
    if hashlib.sha256(blob).hexdigest()!=SHA256:
        raise ValueError("Refusing any executable other than the original 2.1 Beta 2")
    b=bytearray(blob)
    for old,new,firstA,firstB,secondA,secondB in NAMES:
        a,c=swift_small(old),swift_small(new)
        for offsets,segmentA,segmentB in (
            (firstA,a[:8],c[:8]),(firstB,a[:8],c[:8]),
            (secondA,a[8:],c[8:]),(secondB,a[8:],c[8:])):
            patch_group(b,offsets,segmentA,segmentB)
    # About's long UTF-8 social label has 20-byte Swift StaticString count.
    old="Cộng Đồng IOSVN".encode("utf-8")
    off=5866336
    if b[off:off+20]!=old: raise ValueError("Original social label not found")
    b[off:off+20]=b"Telegram"+b"\0"*12
    for offset in (0x42aa0,0x42b60):
        change_imm(b,offset,20,8)
    for off,(old,new) in URLS.items():
        if len(old)!=len(new): raise ValueError("URL must retain UTF-8 byte length")
        if b[off:off+len(old)]!=old.encode(): raise ValueError("Contact offset mismatch "+old)
        b[off:off+len(old)]=new.encode()
    if len(b)!=len(blob): raise ValueError("Binary size changed")
    # Prove no mutations beyond the whitelisted instruction/literal offsets.
    changed={i for i,(old,new) in enumerate(zip(blob,b)) if old!=new}
    allowed=set()
    for _,_,a,c,d,e in NAMES:
        for group in (a,c,d,e):
            for off in group: allowed.update(range(off,off+4))
    allowed.update(range(5866336,5866356))
    allowed.update(range(0x42aa0,0x42aa4))
    allowed.update(range(0x42b60,0x42b64))
    for off,(old,_) in URLS.items():allowed.update(range(off,off+len(old)))
    if not changed<=allowed:raise ValueError("Unexpected executable modifications")
    print("Original binary hash:",SHA256)
    print("About-only binary changed bytes:",len(changed))
    return bytes(b)

def patch_ipa(source,dest):
    with zipfile.ZipFile(source) as z:
        if z.testzip():raise ValueError("Invalid IPA")
        files={item.filename:(z.read(item.filename),item.external_attr)
               for item in z.infolist() if not item.is_dir()}
    p=plistlib.loads(files[APP+"Info.plist"][0])
    for key,val in EXPECTED.items():
        if p.get(key)!=val:raise ValueError("Original iOS identity mismatch: "+key)
    patched=patch_binary(files[APP+"3105"][0])
    files[APP+"3105"]=(patched,files[APP+"3105"][1])
    p["CFBundleName"]=p["CFBundleDisplayName"]="S4NTOS INJECTOR"
    files[APP+"Info.plist"]=(plistlib.dumps(p,fmt=plistlib.FMT_BINARY),files[APP+"Info.plist"][1])
    for lang in ("en","vi","zh-Hans"):
        fn=APP+lang+".lproj/Localizable.strings"
        d=plistlib.loads(files[fn][0])
        d.update(LABELS)
        d["settings.about"]={"en":"About S4NTOS INJECTOR",
        "vi":"Giới thiệu S4NTOS INJECTOR","zh-Hans":"关于 S4NTOS INJECTOR"}[lang]
        d["attribution.title"]=d["settings.about"]
        d["onboarding.welcome_message"]="Developer by S4NTOS INJECTOR"
        files[fn]=(plistlib.dumps(d,fmt=plistlib.FMT_BINARY),files[fn][1])
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,(data,attrs) in files.items():
            zi=zipfile.ZipInfo(name);zi.external_attr=attrs
            zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,data)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert z.read(APP+"3105")==patched
        final=plistlib.loads(z.read(APP+"Info.plist"))
        assert all(final[k]==v for k,v in EXPECTED.items())
        assert final["CFBundleDisplayName"]=="S4NTOS INJECTOR"
    print("PASS: unchanged original version/ID/updater/feed",dest)

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("Usage: patch_original_only.py input-original-branded.ipa output.ipa")
    patch_ipa(sys.argv[1],sys.argv[2])
