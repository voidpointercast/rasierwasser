#!/bin/bash

LOG=$(tempfile)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR="$SCRIPT_DIR/../../.."

echo "Base directory is $BASE_DIR"

echo "Log file is $LOG"

function result() {
  if [ "$1" -eq "0" ]; then
    echo "[OK]"
  else
    echo "[FAIL]"
    cat "$LOG"
  fi
}

echo -n "Cleaning up virtual environment..."
rm -rf /tmp/rasierwasser.env &> "$LOG"
result $?

echo -n "Creating virtual environment..."
virtualenv /tmp/rasierwasser.env &> "$LOG"
result $?

echo -n "Activating virtual environment..."
source /tmp/rasierwasser.env/bin/activate &> "$LOG"
result $?

echo -n "Installing rasierwasser..."
python -m pip install rasierwasser -f "$BASE_DIR/dist" &> "$LOG"
result $?


echo -n "Starting rasierwasser..."
/tmp/rasierwasser.env/bin/rasierwasser --config "$SCRIPT_DIR/rasierwasser.json"& &> "$LOG"
result $?

echo "Starting test phase in 10 seconds"
sleep 10

echo -n "Signing latest rasierwasser wheel"
/tmp/rasierwasser.env/bin/rasierwasser_sign --package-dir "$BASE_DIR" --keyfile-override ./data/key.pem --password TEST --out-dir /tmp/rasierwasser.env &> "$LOG"
result $?

echo -n "Uploading certificate..."
curl -X POST --user alice:bob http://localhost:10010/certificates -d "@$SCRIPT_DIR/data/certificate_upload.json" &> "$LOG"
result $?

echo -n "Uploading file..."
curl -X POST http://localhost:10010/packages -d "@$SCRIPT_DIR/data/package_upload.json" &> "$LOG"
result $?

echo -n "Trying to download uploaded file..."
sleep 2
curl http://localhost:10010/packages/sample/sample_upload_file.txt &> "$LOG"
result $?

echo -n "Uploading latest rasierwasser wheel..."
curl -X POST http://localhost:10010/packages -d "@/tmp/rasierwasser.env/rasierwasser_signature.json" &> "$LOG"
result $?

read -n 1 -p "Hit any key to continue:"


echo "Cleaning up"
RASIERWASSER_PID="$(<rasierwasser.pid)"

echo -n "Stopping rasierwasser..."
kill "$RASIERWASSER_PID" &> "$LOG"
result $?
