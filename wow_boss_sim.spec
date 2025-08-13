# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['wow_boss_sim.py'],
    pathex=[],
    binaries=[],
    datas=[('plan.png', '.')],  # Include plan.png in the same directory as the executable
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WoW_Boss_Simulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# For macOS, create an app bundle
app = BUNDLE(
    exe,
    name='WoW Boss Simulator.app',
    icon=None,
    bundle_identifier='com.example.wowbosssim',
    info_plist={
        'NSHighResolutionCapable': 'True',
    },
)