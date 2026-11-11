# Fraud detection workshop

A hands-on Domino workshop. Train a credit card fraud model as a Domino Job, inspect and register it,
publish it as a REST endpoint, then put a Streamlit app in front of it. Optional steps add two open-model
agents on a GPU (a chat agent that simulates transactions and a LoRA fine-tuned fraud scorer) and a code
assistant. This repository is the whole project: the guides, the code and the data.

## Start here

- **Participants:** open `fraud-workshop-guide.html` in a browser (or `fraud-workshop-guide.pdf`) and follow it. Step 1 shows two ways to get
  the code into a Domino project: fork this repository and create a Git-based project (recommended), or
  upload `support/fraud-workshop-code.zip` into a Domino-hosted project.
- **Administrators:** do `admin-setup-guide.html` (or the PDF) once beforehand (compute environments, hardware tiers,
  optional code assistant environment and Oracle GPU notes).

## What is in this repository

| Path | What it is |
| --- | --- |
| `fraud-workshop-guide.html` | The workshop guide for participants |
| `admin-setup-guide.html` | One-time setup for Domino administrators |
| `fraud-workshop-guide.pdf`, `admin-setup-guide.pdf` | PDF copies of both guides, for when the HTML will not open (restrictions or browser issues) |
| `exercises/` | The exercises: `a_DataExploration` to `f_OpenModelAgents`, with their instructions |
| `.setup/` | Environment files and `unzip_dataset.ipynb`, which puts the raw data in the Domino Dataset |
| `app.sh`, `domino_short_id.py`, `pyproject.toml`, `run.sh` | Project files that Domino jobs and the app use |
| `support/fraud-workshop-data.zip` | The raw transactions (78,324 rows) |
| `support/fraud-workshop-code.zip` | The same code as a zip, for the upload option |
| `support/build_zips.sh` | Rebuilds the code zip from this repository |
| `support/build_pdfs.sh` | Rebuilds both PDFs from the HTML guides (needs Google Chrome) |

Also published as a private Claude artifact: https://claude.ai/artifact/AmfQRdGuyB4uTA4zgwUNqb

## Keeping the zip and PDFs in step

After editing a guide, run `bash support/build_pdfs.sh` and commit the PDFs with it. The code zip is generated from the files in this repository, so edit the files, not the zip. After any
change to the code, run `bash support/build_zips.sh` and commit the new zip with it.

## Using Git in Domino

A Git-based project reads its code from your fork, but its Domino Dataset is separate and starts empty.
Run `.setup/unzip_dataset.ipynb` once to copy the data from `support/`
into the dataset. After you change a file, commit and push so Jobs and the app pick it up.
