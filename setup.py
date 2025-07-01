OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icons/pabrowser.icns',
    'no_compress': True,
    'skip_codesign': True,
    'includes': ['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebChannel', 'PyQt5.QtWebEngineCore'],
    'plist': {
        'CFBundleName': 'PaBrowser',
        'CFBundleDisplayName': 'PaBrowser',
        'CFBundleIdentifier': 'com.pablodev.pabrowser',
        'CFBundleVersion': '1.0',
        'CFBundleShortVersionString': '1.0',
    },
}
