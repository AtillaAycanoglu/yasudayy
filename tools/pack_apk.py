#!/usr/bin/env python3
"""
Builds an unsigned APK without the Android SDK / aapt2.

It writes the binary AndroidManifest.xml (AXML) and a minimal resources.arsc
(one drawable: the launcher icon) by hand, then zips them together with
classes.dex and the web assets, 4-byte aligning every stored entry.

usage: pack_apk.py <classes.dex> <assets_dir> <icon.png> <out.apk>
"""
import os
import struct
import sys
import zipfile
import zlib

PACKAGE = "com.pirpir.game"
ACTIVITY = "com.pirpir.game.MainActivity"
LABEL = "Pırpır"
VERSION_CODE = 1
VERSION_NAME = "1.0"
MIN_SDK = 24
TARGET_SDK = 34

ICON_RES_ID = 0x7F010000          # package 0x7f, type 1 (drawable), entry 0
THEME_FULLSCREEN = 0x01030007     # @android:style/Theme.NoTitleBar.Fullscreen
ANDROID_NS = "http://schemas.android.com/apk/res/android"

# android attribute resource ids
ATTR = {
    "theme": 0x01010000, "label": 0x01010001, "icon": 0x01010002, "name": 0x01010003,
    "exported": 0x01010010, "screenOrientation": 0x0101001E, "configChanges": 0x0101001F,
    "minSdkVersion": 0x0101020C, "versionCode": 0x0101021B, "versionName": 0x0101021C,
    "targetSdkVersion": 0x01010270, "hardwareAccelerated": 0x010102D3,
}

T_REF, T_STRING, T_DEC, T_HEX, T_BOOL = 0x01, 0x03, 0x10, 0x11, 0x12


# ---------------------------------------------------------------- string pool
def string_pool(strings, utf8=False):
    data = b""
    offsets = []
    for s in strings:
        offsets.append(len(data))
        if utf8:
            b = s.encode("utf-8")
            def ln(n):
                return bytes([n]) if n < 0x80 else bytes([(n >> 8) | 0x80, n & 0xFF])
            data += ln(len(s)) + ln(len(b)) + b + b"\x00"
        else:
            u = s.encode("utf-16-le")
            data += struct.pack("<H", len(u) // 2) + u + b"\x00\x00"
    while len(data) % 4:
        data += b"\x00"
    header_size = 28
    strings_start = header_size + 4 * len(strings)
    size = strings_start + len(data)
    flags = 0x100 if utf8 else 0
    hdr = struct.pack("<HHIIIIII", 0x0001, header_size, size, len(strings), 0, flags, strings_start, 0)
    return hdr + b"".join(struct.pack("<I", o) for o in offsets) + data


# ---------------------------------------------------------------- AXML
class Axml:
    def __init__(self):
        self.attr_names = []   # strings that carry a resource id (must come first in the pool)
        self.strings = []
        self.events = []

    def _idx(self, s):
        if s in self.strings:
            return self.strings.index(s)
        self.strings.append(s)
        return len(self.strings) - 1

    def start(self, tag, attrs):
        self.events.append(("start", tag, attrs))

    def end(self, tag):
        self.events.append(("end", tag))

    def build(self):
        # collect attribute names with ids first, in resource-id order
        names = []
        for ev in self.events:
            if ev[0] == "start":
                for (ns, name, _t, _v) in ev[2]:
                    if ns and name not in names:
                        names.append(name)
        names.sort(key=lambda n: ATTR[n])
        self.strings = list(names)
        resmap = [ATTR[n] for n in names]
        ns_prefix, ns_uri = self._idx("android"), self._idx(ANDROID_NS)

        body = b""
        body += struct.pack("<HHIIiII", 0x0100, 16, 24, 1, -1, ns_prefix, ns_uri)
        for ev in self.events:
            if ev[0] == "start":
                _, tag, attrs = ev
                # attributes with ids sorted by id, plain ones afterwards
                attrs = sorted(attrs, key=lambda a: (0, ATTR[a[1]]) if a[0] else (1, a[1]))
                ab = b""
                for (ns, name, typ, val) in attrs:
                    ns_i = ns_uri if ns else 0xFFFFFFFF
                    name_i = self._idx(name)
                    if typ == T_STRING:
                        si = self._idx(val)
                        raw, data = si, si
                    else:
                        raw, data = 0xFFFFFFFF, val & 0xFFFFFFFF
                    ab += struct.pack("<IIIHBBI", ns_i, name_i, raw, 8, 0, typ, data)
                tag_i = self._idx(tag)
                ext = struct.pack("<IIHHHHHH", 0xFFFFFFFF, tag_i, 20, 20, len(attrs), 0, 0, 0)
                chunk = ext + ab
                body += struct.pack("<HHIIi", 0x0102, 16, 16 + len(chunk), 1, -1) + chunk
            else:
                chunk = struct.pack("<II", 0xFFFFFFFF, self._idx(ev[1]))
                body += struct.pack("<HHIIi", 0x0103, 16, 24, 1, -1) + chunk
        body += struct.pack("<HHIIiII", 0x0101, 16, 24, 1, -1, ns_prefix, ns_uri)

        sp = string_pool(self.strings)
        rm = struct.pack("<HHI", 0x0180, 8, 8 + 4 * len(resmap)) + b"".join(struct.pack("<I", r) for r in resmap)
        payload = sp + rm + body
        return struct.pack("<HHI", 0x0003, 8, 8 + len(payload)) + payload


def manifest():
    A = True
    x = Axml()
    x.start("manifest", [
        (A, "versionCode", T_DEC, VERSION_CODE),
        (A, "versionName", T_STRING, VERSION_NAME),
        (None, "package", T_STRING, PACKAGE),
    ])
    x.start("uses-sdk", [(A, "minSdkVersion", T_DEC, MIN_SDK), (A, "targetSdkVersion", T_DEC, TARGET_SDK)])
    x.end("uses-sdk")
    x.start("uses-permission", [(A, "name", T_STRING, "android.permission.VIBRATE")])
    x.end("uses-permission")
    x.start("application", [
        (A, "theme", T_REF, THEME_FULLSCREEN),
        (A, "label", T_STRING, LABEL),
        (A, "icon", T_REF, ICON_RES_ID),
        (A, "hardwareAccelerated", T_BOOL, 0xFFFFFFFF),
    ])
    x.start("activity", [
        (A, "name", T_STRING, ACTIVITY),
        (A, "exported", T_BOOL, 0xFFFFFFFF),
        (A, "screenOrientation", T_DEC, 1),          # portrait
        (A, "configChanges", T_HEX, 0x04A0),         # orientation|keyboardHidden|screenSize
    ])
    x.start("intent-filter", [])
    x.start("action", [(A, "name", T_STRING, "android.intent.action.MAIN")])
    x.end("action")
    x.start("category", [(A, "name", T_STRING, "android.intent.category.LAUNCHER")])
    x.end("category")
    x.end("intent-filter")
    x.end("activity")
    x.end("application")
    x.end("manifest")
    return x.build()


# ---------------------------------------------------------------- resources.arsc
def resources(icon_path):
    global_pool = string_pool([icon_path], utf8=True)
    type_pool = string_pool(["drawable"], utf8=True)
    key_pool = string_pool(["icon"], utf8=True)

    spec = struct.pack("<HHIBBHI", 0x0202, 16, 16 + 4, 1, 0, 0, 1) + struct.pack("<I", 0)

    config = struct.pack("<I", 64) + b"\x00" * 60
    entries_count = 1
    header_size = 8 + 4 + 4 + 4 + len(config)          # 84
    entries_start = header_size + 4 * entries_count
    entry = struct.pack("<HHI", 8, 0, 0) + struct.pack("<HBBI", 8, 0, T_STRING, 0)
    typ = struct.pack("<HHIBBHII", 0x0201, header_size, entries_start + len(entry), 1, 0, 0, entries_count, entries_start)
    typ += config + struct.pack("<I", 0) + entry

    pkg_header = 288
    name = "com.pirpir.game".encode("utf-16-le").ljust(256, b"\x00")
    type_off = pkg_header
    key_off = type_off + len(type_pool)
    pkg_body = type_pool + key_pool + spec + typ
    pkg = struct.pack("<HHII", 0x0200, pkg_header, pkg_header + len(pkg_body), 0x7F) + name
    pkg += struct.pack("<IIIII", type_off, 1, key_off, 1, 0) + pkg_body
    assert len(pkg) == pkg_header + len(pkg_body)

    body = global_pool + pkg
    return struct.pack("<HHII", 0x0002, 12, 12 + len(body), 1) + body


# ---------------------------------------------------------------- zip (aligned)
def write_apk(out, entries):
    """entries: list of (name, bytes, compress). Stored entries are 4-byte aligned."""
    with open(out, "wb") as f:
        central = b""
        for name, data, compress in entries:
            nb = name.encode("utf-8")
            crc = zlib.crc32(data) & 0xFFFFFFFF
            if compress:
                co = zlib.compressobj(9, zlib.DEFLATED, -15)
                payload = co.compress(data) + co.flush()
                method = 8
            else:
                payload, method = data, 0
            offset = f.tell()
            extra = b""
            if method == 0:
                pad = (4 - (offset + 30 + len(nb)) % 4) % 4
                extra = b"\x00" * pad
            dostime, dosdate = 0, (2026 - 1980) << 9 | 1 << 5 | 1
            flags = 0x800
            f.write(struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, flags, method, dostime, dosdate, crc,
                                len(payload), len(data), len(nb), len(extra)) + nb + extra + payload)
            central += struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, flags, method, dostime, dosdate, crc,
                                   len(payload), len(data), len(nb), 0, 0, 0, 0, 0, offset) + nb
        cd_off = f.tell()
        f.write(central)
        f.write(struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, len(entries), len(entries), len(central), cd_off, 0))


def main():
    dex, assets_dir, icon, out = sys.argv[1:5]
    icon_path = "res/drawable/icon.png"
    entries = [
        ("AndroidManifest.xml", manifest(), True),
        ("classes.dex", open(dex, "rb").read(), True),
        ("resources.arsc", resources(icon_path), False),   # must be stored + aligned (targetSdk >= 30)
        (icon_path, open(icon, "rb").read(), False),
    ]
    for root, _, files in os.walk(assets_dir):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, assets_dir).replace(os.sep, "/")
            entries.append(("assets/" + rel, open(p, "rb").read(), True))
    write_apk(out, entries)
    print("wrote", out)


if __name__ == "__main__":
    main()
