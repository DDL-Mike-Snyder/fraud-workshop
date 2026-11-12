# Fraud workshop resources

This repository only hosts the files that the Applied Domino Workshop downloads with `curl`. The workshop itself (guides,
sign-in, and the source of these files) lives in the Applied Domino Workshop app and its repository.

| File | What it is |
| --- | --- |
| [`resources/start_here.ipynb`](resources/start_here.ipynb) | Run first in a Domino workspace. Downloads the two zips below into your project. |
| [`resources/fraud-workshop-code.zip`](resources/fraud-workshop-code.zip) | Exercises, scripts, the Streamlit app and the environment check |
| [`resources/fraud-workshop-data.zip`](resources/fraud-workshop-data.zip) | The raw credit card transactions (`raw_cc_transactions.csv.gz`) |

From a Domino workspace terminal:

```
curl -fSL -O https://raw.githubusercontent.com/DDL-Mike-Snyder/fraud-workshop/main/resources/start_here.ipynb
```

Do not edit these files here. They are generated and published from the workshop repository with
`scripts/publish_resources.sh`. The previous contents of this repository are in its git history.
