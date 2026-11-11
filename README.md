# Fraud detection workshop

A hands-on Domino workshop. Train a credit card fraud model as a Domino Job, inspect and register it, publish it
as a REST endpoint, then put a Streamlit app in front of it. Optional steps add two open-model agents on a GPU and
a code assistant.

## Where to go

| You are | Go to | What you will find |
| --- | --- | --- |
| **Taking the workshop** | [`user/`](user/) | The participant guide (HTML and PDF) and the files to download |
| **A Domino administrator** | [`admin/`](admin/) | The one-time setup guide (HTML and PDF) and the environment Dockerfiles |

Administrators go first: participants need the environments and hardware tiers that the admin guide creates.

## The rest of this repository

The files at the top level are the Domino project itself. Domino runs a Git-based project from the repository
root, so `exercises/`, `app.sh` and the others have to stay here. Participants do not need to open them to follow
the guide.

| Path | What it is |
| --- | --- |
| `exercises/` | The exercises, `a_DataExploration` to `f_OpenModelAgents`, with their instructions |
| `.setup/` | `verify_environment.py`, `unzip_dataset.ipynb` (loads the raw data into the Domino Dataset) and setup notes |
| `app.sh`, `domino_short_id.py`, `pyproject.toml`, `run.sh`, `__init__.py`, `artifacts/` | Project files that Jobs and the app use |
| `tools/` | For whoever maintains this repository: `build_zips.sh` and `build_pdfs.sh` |

Also published as a private Claude artifact: https://claude.ai/artifact/AmfQRdGuyB4uTA4zgwUNqb

## Maintaining it

- After editing a guide, run `bash tools/build_pdfs.sh` (needs Google Chrome) and commit the PDFs with it.
- The code zip is generated from the project files, so edit the files, not the zip. After any code change, run
  `bash tools/build_zips.sh` and commit the new zip with it.
- A Git-based project has its own empty Domino Dataset. `.setup/unzip_dataset.ipynb` copies the data from
  `user/downloads/` into it, once.
