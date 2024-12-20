# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['leia.py'],
    pathex=[],
    binaries=[('d:/projects/leia-0.4.0/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.core.dll', 'azure/cognitiveservices/speech'), ('d:/projects/leia-0.4.0/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.audio.sys.dll', 'azure/cognitiveservices/speech'), ('d:/projects/leia-0.4.0/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.codec.dll', 'azure/cognitiveservices/speech'), ('d:/projects/leia-0.4.0/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.kws.dll', 'azure/cognitiveservices/speech'), ('d:/projects/leia-0.4.0/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.lu.dll', 'azure/cognitiveservices/speech')],
    datas=[('files/*', 'files/'), ('files/images/*', 'files/images/'), ('.env', '.')],
    hiddenimports=['azure.cognitiveservices.speech'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['vosk'],
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
    name='leia',
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
