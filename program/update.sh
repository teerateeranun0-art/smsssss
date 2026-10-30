TARGET="$PREFIX/bin/RUN-SMS-WEB"
SOURCE="setup/SMS-RUN-WEB-TERMUX.sh"

echo "[*] updating..."
cd
rm -rf ~/SMS-Spam
git clone https://github.com/teerateeranun0-art/sms-spam.git
cd SMS-Spam

if ! command -v python >/dev/null 2>&1; then
    echo "[*] cannot find Python..."
    pkg update -y
    pkg install python -y
else
    echo "[OK] Python found"
fi

if ! command -v pip >/dev/null 2>&1; then
    echo "[*] cannot find pip -> installing..."
    pkg install python-pip -y
else
    echo "[OK] pip found"
fi
echo "[*] updating from requirements.txt"

pip install -r setup/requirements.txt

echo "[*] installing RUN-SMS-WEB ..."
mv "$SOURCE" "$TARGET"
chmod +x "$TARGET"
echo "[OK] installation of RUN-SMS-WEB completed!"
echo "[*] deleting installation files..."
rm -rf setup
rm -rf assets
rm -f install-termux.sh
rm -f README.md
echo "[OK] deleted installation files successfully!"
echo "[*] Update completed!"
