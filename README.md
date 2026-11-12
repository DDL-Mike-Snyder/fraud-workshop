# Fraud workshop resources

| File | What it is |
| --- | --- |
| [`resources/start_here.ipynb`](resources/start_here.ipynb) | Setup notebook. Run it once in a Domino workspace: it downloads the two zips below, unzips the code into the project, puts the raw data in the project's Domino Dataset, and checks the environment. |
| [`resources/fraud-workshop-code.zip`](resources/fraud-workshop-code.zip) | Workshop code: the exercises, training scripts, Streamlit app, open-model agents and the environment check (`.setup/verify_environment.py`). |
| [`resources/fraud-workshop-data.zip`](resources/fraud-workshop-data.zip) | Raw data: `raw_cc_transactions.csv.gz`, 78,324 credit card transactions. |

Download any file with `curl`, for example from a Domino workspace terminal:

```
curl -fSL -O https://raw.githubusercontent.com/DDL-Mike-Snyder/fraud-workshop/main/resources/start_here.ipynb
```
