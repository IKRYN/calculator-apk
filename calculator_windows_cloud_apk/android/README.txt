# APK сборка через WSL (Ubuntu)
1. Windows PowerShell от администратора: `wsl --install -d Ubuntu`; перезапустите ПК и откройте Ubuntu.
2. В Ubuntu:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk build-essential autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev cmake libffi-dev libssl-dev
mkdir -p ~/calculator
```
3. Скопируйте файлы `main.py` и `buildozer.spec` из папки android архива в `~/calculator` (Проводник Windows: `\\wsl$\Ubuntu\home\ВАШ_ПОЛЬЗОВАТЕЛЬ\calculator`).
4. В Ubuntu:
```bash
cd ~/calculator
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer cython==0.29.36
buildozer android debug
```
5. APK появится в папке `bin/`. Скопируйте его на телефон и установите, разрешив Android установку из данного источника.
