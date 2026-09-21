#!/usr/bin/env bash
set -euo pipefail

echo "Creating local virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
else
  echo ".env already exists"
fi

echo
echo "Downloading and validating the Kaggle dataset..."
python prepare_dataset.py

echo
echo "Running the full offline application pipeline..."
python3 main.py

echo
echo "Setup complete."
echo "Results are in: outputs/dataset_round_01"
echo "Use: source .venv/bin/activate"
echo "Then: python3 main.py"
echo
echo "Downloading and validating the Kaggle dataset..."
python prepare_dataset.py

