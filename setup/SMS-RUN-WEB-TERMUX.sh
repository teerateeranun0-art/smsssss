

PROJECT_DIR="$HOME/SMS-Spam"

if [ ! -d "$PROJECT_DIR" ]; then
    echo " Error: Cannot access $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR" || exit

# ==========================================
# auto-update check
# ==========================================
echo " Checking for updates..."

git fetch origin > /dev/null 2>&1

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "  New update found!"
    echo " System is updating automatically..."
    
    if [ -f "program/update.sh" ]; then
        bash program/update.sh
        
        echo " Update completed! Please run the RUN-SMS-WEB command again"
        exit 0
    else
        echo " File not found: program/update.sh Skipping update..."
    fi
else
    echo " System is up to date"
fi

# ==========================================
# run the web server
# ==========================================
echo " Starting SMS-Spam Web Server..."
cd web || exit
python RUN-WEB.py
