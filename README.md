# Fraud detection workshop

A hands-on Domino workshop. Train a credit card fraud model as a Domino Job, inspect and register it, publish it
as a REST endpoint, then put a Streamlit app in front of it. Optional steps add two open-model agents on a GPU and
a code assistant.

| You are | Go to | What is there |
| --- | --- | --- |
| **A Domino administrator** | [`admin/`](admin/) | The one-time setup guide (HTML and PDF). Do this first. |
| **Taking the workshop** | [`user/`](user/) | The workshop guide (HTML and PDF) and the two zip files you work from |
| **Maintaining this repository** | [`domino/`](domino/) | The workshop's code and the scripts that build the zip and the PDFs |

The guides are meant to be read in a browser. If the HTML will not open, use the PDF next to it.

Also published as a private Claude artifact: https://claude.ai/artifact/AmfQRdGuyB4uTA4zgwUNqb

## Maintaining it

- The code zip is built from `domino/project/`, so edit the files there, not the zip. After any change run
  `bash domino/build_zips.sh` and commit the new zip.
- After editing a guide, run `bash domino/build_pdfs.sh` (needs Google Chrome) and commit the PDFs.
