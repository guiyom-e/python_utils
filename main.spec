# -*- mode: python -*-

block_cipher = None

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
import distutils
if distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

a = Analysis(['main.py'],
             pathex=['.'],  # TODO: path to set
             binaries=[],
             datas=[('tools', 'tools/')], # if needed, also add: ('tools/venv/Lib/site-packages/pptx/templates/default.pptx', 'pptx/templates/')
             hiddenimports = [],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, icon='tools\\favicon.ico')
