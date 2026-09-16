$ErrorActionPreference = 'Stop'
python -m pip install --upgrade pyinstaller pillow
python .\tools\make_icon.py
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Quarry --icon assets/icon.ico quarry_desktop.pyw
Write-Host "Built dist\Quarry.exe"
