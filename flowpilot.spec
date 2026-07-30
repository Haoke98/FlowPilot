# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for FlowPilot standalone binary
# 构建: pyinstaller --clean --onefile flowpilot.spec
# 输出: dist/pflowc

a = Analysis(
    ['__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('PFlowC/utils/Country.mmdb', 'PFlowC/utils')],
    hiddenimports=['colorlog', 'geoip2', 'geoip2.database', 'dns', 'dns.resolver'],
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
    a.binaries,
    a.datas,
    [],
    name='pflowc',
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
