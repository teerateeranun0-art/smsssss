#!/data/data/com.termux/files/usr/bin/bash

echo "=== INSTALL SCRIPT FOR SMS-SPAM WEB ==="


if ! command -v python >/dev/null 2>&1; then
    echo "[*] don't find Python -> installing..."
    pkg update -y
    pkg install python -y
else
    echo "[OK] Python found"
fi


if ! command -v pip >/dev/null 2>&1; then
    echo "[*] don't find pip -> installing..."
    pkg install python-pip -y 
else
    echo "[OK] pip found"
fi


REQ_FILE="setup/requirements.txt"

if [ ! -f "$REQ_FILE" ]; then
    echo "[!] don't find $REQ_FILE"
    exit 1
fi

echo "[*] installing dependencies from $REQ_FILE..."
pip install -r "$REQ_FILE"

if [ $? -eq 0 ]; then
    echo "[OK] installed dependencies"
else
    echo "[!] an error occurred while installing dependencies"
    exit 1
fi


TARGET="$PREFIX/bin/RUN-SMS-WEB"
SOURCE="setup/SMS-RUN-WEB-TERMUX.sh"

if [ ! -f "$SOURCE" ]; then
    echo "[!] don't find file $SOURCE for creating run command"
else
    echo "[*] installing run command ..."
    mv "$SOURCE" "$TARGET"
    chmod +x "$TARGET"
    echo "[OK] installation complete!"
fi


echo "[*] cleaning up installation files..."
rm -f install-termux.sh
rm -rf setup
rm -f README.md
rm -rf assets

echo "[OK] Cleanup complete!"
sleep 0.5
echo "[OK] Installation complete!"
sleep 1

clear
echo "#################################################"
echo "#                                               #"
echo "#           คำอธิบาย โปรดอ่าน !!!                 #"
echo "#        (EXPLANATION : PLEASE READ)            #"
echo "#                                               #"
echo "#################################################"
echo ""
read -p ">>> press Enter to continue..."

clear
echo "#################################################"
echo "#                                               #"
echo "#             ขอขอบคุณที่ใช้งานสคริปต์นี้             #"
echo "#                 (THANK YOU)                   #"
echo "#                by @tp_1092s                   #" 
echo "#################################################"
echo ""
read -p ">>> press Enter to continue..."

clear
echo "================================================="
echo "                   manual                        "
echo "================================================="
echo ""
echo " system components:"
echo "   1. SMS-Fast.py  -> file for fast SMS bombing"
echo "   2. SMS-Slow.py  -> file for slow SMS bombing"
echo "   3. SMS-Super.py -> file for super fast SMS bombing"
echo "   4. API_LIST.py  -> file for API list"
echo "   5. RUN-WEB.py   -> file for web interface"
echo "   6. index.html   -> main web page file"
echo "   7. favicon.jpg  -> website favicon"
echo "   8. update.sh    -> used for updating the program"
echo "   9. API-Test.py  -> used for testing the API"
echo ""
echo " update:"
echo "run command: bash ~/SMS-Spam/program/update.sh"
echo ""
echo " API Testing"
echo "run command: python ~/SMS-Spam/program/API-Test.py"
echo ""
echo "-------------------------------------------------"
echo " running methods:"
echo "-------------------------------------------------"
echo ""
echo "option 1: run via web interface"
echo "   run command: RUN-SMS-WEB"
echo "   (and go to http://localhost:8080)"
echo ""
echo "option 2: run via terminal"
echo "   1. navigate to the program directory:"
echo "      cd program"
echo ""
echo "   2. run the desired script:"
echo "      - fast bombing: python SMS-Fast.py"
echo "      - slow bombing: python SMS-Slow.py"
echo "      - super fast bombing: python SMS-Super.py"
echo ""
echo "================================================="
sleep 1
echo "[OK] Installation complete!"
echo "================================================="
