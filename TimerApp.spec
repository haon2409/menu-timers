# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['timers.py'],
    pathex=[],
    binaries=[],
    datas=[('alert.mp3', '.'), ('icon64.png', '.'), ('Info.plist', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TimerApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon64.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TimerApp',
)
app = BUNDLE(
    coll,
    name='TimerApp.app',
    icon='icon64.png',
    bundle_identifier='com.yourcompany.timerapp',
)
