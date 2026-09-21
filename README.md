# Apartment Clones + SwarmUI MVP

A small Python client for testing our apartment-rendering prototype with either:

- an offline mock generator, for testing the project without SwarmUI
- a real SwarmUI instance, for image generation

The project now uses external libraries for cleaner setup and nicer output:

- `requests` for HTTP calls to SwarmUI
- `python-dotenv` for `.env` API keys and local config overrides
- `rich` for readable CLI tables and JSON output

## Quick Start

### Windows PowerShell

```powershell
.\setup_windows.ps1
```

Setup installs dependencies, downloads the Kaggle dataset, validates the image
files, and writes a dataset manifest under `data\processed\`. Before running
setup, configure Kaggle authentication for the `kagglehub` package. The
dataset cannot be downloaded anonymously. No manual dataset download or
preprocessing step is needed after that.

Use Kaggle's documented authentication method, such as a local Kaggle token
configuration or the `KAGGLE_API_TOKEN` environment variable. Keep the token
outside the repository and never commit it to `.env` or source files.

For an offline code-only setup that skips the dataset download:

```powershell
.\setup_windows.ps1 -SkipDataset
```

The setup script runs the full offline application pipeline after installation.
It does not run the smoke test unless you explicitly request it:

```powershell
.\setup_windows.ps1 -RunSmokeTest
```

After setup, the complete offline demo can be run with:

```powershell
python3 main.py
```

When the dataset manifest exists, this command runs the full existing-image
pipeline without SwarmUI or image generation. It selects dataset images,
builds the buyer profile, writes prompts and result metadata, and saves the
selected images under `outputs\dataset_round_01\`. Choices are recorded in
`data\dataset_session.json`.

After reviewing the copied images, set each candidate's `choice` to `like`,
`dislike`, or `skip` in `data\dataset_session.json`. Then run `python3 main.py`
again. The next run reuses those choices when updating the profile and selecting
the next dataset candidates.

If no dataset manifest exists, it falls back to the offline demo and writes
placeholder candidate images to `outputs\round_01\`.

Then run:

```powershell
. .\.venv\Scripts\Activate.ps1
python main.py check --mock
python main.py demo --mock --images 2
```

The PowerShell runner runs the full offline pipeline, starts the web interface,
and opens it in your browser without activating the environment:

```powershell
.\run_windows.ps1
```

The interface is available at [http://localhost:5000](http://localhost:5000).
Use `-NoBrowser` if you want to start it without opening a browser window:

```powershell
.\run_windows.ps1 -NoBrowser
```

Run the smoke test explicitly when you need validation only:

```powershell
.\run_windows.ps1 -RunSmokeTest
```

For an explicit command, call the project interpreter directly:

```powershell
& ".\.venv\Scripts\python.exe" main.py demo --mock --images 2
```

If PowerShell blocks local scripts because of the execution policy, allow them
for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### macOS/Linux

```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

Then run:

```bash
source .venv/bin/activate
python main.py check --mock
python main.py demo --mock --images 2
```

## Manual Setup

```powershell
python -m venv .venv
```

Activate it:

```powershell
. .\.venv\Scripts\Activate.ps1
```

or:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create local environment settings:

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Run the offline preflight:

```bash
python smoke_test.py
```

## Configuration And API Keys

Default non-secret settings live in `config.json`.

Local machine settings and secrets live in `.env`. Do not commit `.env`; it is ignored by Git.

Important `.env` values:

- `SWARM_URL`: SwarmUI URL, usually `http://localhost:7801`
- `SWARM_API_KEY`: optional API key for a protected SwarmUI proxy or hosted endpoint
- `SWARM_MODEL`: optional model override
- `MOCK_SWARM`: set to `true` to use mock mode by default
- `IMAGES_PER_ROUND`: default number of candidates
- `IMAGE_WIDTH` / `IMAGE_HEIGHT`: generation size
- `GENERATION_STEPS`, `CFG_SCALE`, `GENERATION_SEED`: generation parameters
- `NEGATIVE_PROMPT`: shared negative prompt

`SWARM_API_KEY` is sent as:

```text
Authorization: Bearer YOUR_KEY
```

Local SwarmUI usually does not need an API key, so leave it blank unless your setup requires one.

Check the resolved config, with the API key redacted:

```bash
python main.py config
```

## Test Without SwarmUI

Use mock mode to test everything except real image generation:

```bash
python smoke_test.py
python main.py check --mock
python main.py demo --mock --images 2
```

Mock mode uses the same profile, prompt, round, JSON output, and image-download flow as the real client. It writes deterministic placeholder PNGs instead of generated images.

Mock demo artifacts are written under:

```text
outputs/round_01/
```

You can also set this in `.env`:

```text
MOCK_SWARM=true
```

Then you can omit `--mock`.

## Kaggle Dataset

The [Interior Design Styles dataset](https://www.kaggle.com/datasets/stepanyarullin/interior-design-styles)
is downloaded and validated automatically by the setup script. It contains
about 18,600 interior images grouped into 19 style classes, with separate
training and test folders and test labels.

The dataset is comparable to the style-profile part of this MVP, but it is not
an automatic replacement for SwarmUI. The current project expects each swipe
to contain a buyer choice and semantic tags such as `warm`, `natural_wood`, or
`minimal`. The Kaggle labels are broader style classes, so they must be mapped
to project tags before they can be used as swipes. The current code does not
automatically inspect or classify the downloaded images.

The setup process creates a manifest containing each valid image path, split,
style, dimensions, and image mode. It does not duplicate the 732 MB download
inside the repository. Also check the dataset terms before redistributing the
images: the page notes that they were scraped from Houzz.com.

When using the dataset, keep it outside the repository or under an ignored
directory such as `data\kaggle\`, then add selected labeled examples to
`data\session.json`. The normal profile command remains:

```powershell
python3 main.py profile --input data\session.json
```

Automatic dataset indexing is implemented through `prepare_dataset.py`.
Automatic image classification, semantic-tag mapping, and training a local
image generator are not currently implemented.

To run the existing-image pipeline explicitly:

```powershell
python3 main.py dataset --images 5
```

This command never calls SwarmUI and never generates new images. It only copies
selected images from the downloaded dataset into a results round and produces
the metadata needed for manual candidate choices.

## Run With SwarmUI

The no-argument command remains offline. After installing SwarmUI, set
`MOCK_SWARM=false` in `.env`, then use the explicit SwarmUI commands below.

Start SwarmUI and make sure the web UI opens at:

```text
http://localhost:7801
```

Check the connection:

```bash
python main.py check
```

Run the included demo:

```bash
python main.py demo
```

Use a different URL:

```bash
python main.py check --url http://127.0.0.1:7801
```

Override the model:

```bash
python main.py round --input data/session.json --model "YOUR_SWARM_MODEL_NAME"
```

## Main Workflow

## Image Review Web Interface

After creating a dataset round, start the local review interface with Docker if
you want to use containers:

```powershell
docker compose up --build
```

Open [http://localhost:5000](http://localhost:5000). The interface loads the
latest `dataset_round_*`, displays the existing images, and lets you save
`like`, `dislike`, `skip`, and 1--5 ratings. Feedback is persisted in
`data\dataset_session.json` through the mounted project volume.

Click **Next round** in the interface after reviewing the images. It runs the
dataset pipeline using your saved choices, creates the next
`outputs\dataset_round_*` folder, and refreshes the page with the new images.
Previously shown dataset images are excluded until the available dataset has
been exhausted. It does not contact SwarmUI or generate new images.

Stop the interface with:

```powershell
docker compose down
```

The web interface does not generate images or contact SwarmUI.

Docker is optional. The recommended Windows command is `.run_windows.ps1`,
which runs the same interface directly with the project virtual environment.

Edit:

```text
data/session.json
```

The important parts are:

- `buyer`: short natural-language intake
- `swipes`: liked/disliked image concepts
- `room`: the apartment/room description
- `rounds`: generated candidate rounds

Build the transparent taste profile:

```bash
python main.py profile --input data/session.json
```

Generate a round:

```bash
python main.py round --input data/session.json
```

Generate fewer candidates while testing:

```bash
python main.py round --input data/session.json --images 2
```

Show a session file:

```bash
python main.py show --input data/session.json
```

## Outputs

Each round writes:

- `prompts.json`
- `generation_results.json`
- generated image files, or placeholder PNGs in mock mode
- `profile.json`

This makes it possible to inspect exactly what was sent to SwarmUI or the mock client.

## Selecting Candidates

After a round, open the generated images and record your choices in `data/session.json`:

```json
{
  "candidate_id": "c3",
  "choice": "like"
}
```

Allowed values:

- `like`
- `dislike`
- `skip`

Then run another round:

```bash
python main.py round --input data/session.json
```

## Project Boundary

Implemented:

1. short buyer intake
2. swipe representation
3. transparent taste-vector extraction
4. five deliberately varied candidates per round
5. SwarmUI API generation
6. offline mock generation
7. `.env` configuration and optional API-key header
8. saved experiment artifacts

Not yet implemented:

- real CLIP/IP-Adapter based preference embeddings
- a trained or LLM-based pairwise buyer judge
- ControlNet structure locking against a real apartment image
- automated segmentation/IoU fidelity gate
- PickScore or another validated image preference metric
- clone-in-the-loop optimization
- 2AFC human study
- DPO/LoRA training

Those should be added as separate research components instead of being hidden behind a fake score.

## Troubleshooting

### Missing dependency

Run:

```bash
python -m pip install -r requirements.txt
```

### Could not connect to SwarmUI

Start SwarmUI first and confirm this opens in your browser:

```text
http://localhost:7801
```

If you are intentionally testing without SwarmUI, add `--mock` or set `MOCK_SWARM=true` in `.env`.

### No model was detected

Open the SwarmUI Generate tab and confirm that at least one text-to-image model is available. You can also set `SWARM_MODEL` in `.env`, set `model` in `config.json`, or pass `--model`.

### Generation fails with a model error

Model names depend on what is installed in your SwarmUI instance. Run:

```bash
python main.py check
```

Then use one of the reported model names.

## SwarmUI API Basis

This client uses SwarmUI's documented HTTP API:

- `POST /API/GetNewSession`
- `POST /API/GetCurrentStatus`
- `POST /API/ListT2IParams`
- `POST /API/GenerateText2Image`

Official documentation:

- https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/API.md
- https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/APIRoutes/T2IAPI.md
- https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/Basic%20Usage.md
