# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
SETUP_DIR = 'C:\\Users\\soari\\OneDrive\\myGitHubProjects\\easypoi'

a = Analysis(['easypoi.py'],
             pathex=['C:\\Users\\soari\\OneDrive\\myGitHubProjects\\easypoi'],
             binaries=[],
             datas=[(SETUP_DIR+'\\data','data'),(SETUP_DIR+'\\themes','themes'),(SETUP_DIR+'\\poi_spider','poi_spider'),(SETUP_DIR+'\\html','html')],
             hiddenimports=[],
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
          [],
          exclude_binaries=True,
          name='easypoi',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='C:\\Users\\soari\\OneDrive\\myGitHubProjects\\easypoi\\favicon.ico'
           )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='easypoi')
