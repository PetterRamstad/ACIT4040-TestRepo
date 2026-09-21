#!/usr/bin/env bash
set -e
if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo "Apartment SwarmUI MVP"
echo
echo "Offline preflight without SwarmUI."
$PYTHON smoke_test.py
$PYTHON main.py check --mock
echo
echo "Mock demo: $PYTHON main.py demo --mock --images 2"
echo "Real SwarmUI later: $PYTHON main.py check && $PYTHON main.py demo"
