# Windows EXE
Скопируйте ваш текущий tkinter main.py в эту папку. Откройте CMD в папке (адресная строка Проводника: cmd), затем:
```bat
py -m pip install --upgrade pip
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Calculator main.py
```
Готовый файл: dist\Calculator.exe
