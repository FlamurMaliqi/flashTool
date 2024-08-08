import PyInstaller.__main__

PyInstaller.__main__.run([
    'view.py',
    '--onefile',
    '--clean',
    '--windowed'
])