# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    hiddenimports=['pyqtspinner'],
    binaries=[],
    datas=[('loading.gif', '.')],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f"LDOT2-{version}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
