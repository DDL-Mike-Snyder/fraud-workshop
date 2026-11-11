# Fraud Detection Workshop Setup

If you're working from a project created off the workshop Template, the Compute Environment is already attached and configured — `environment.md` documents the spec, useful if you ever want to rebuild or modify it, but you shouldn't need to touch it to get started.

The one thing that doesn't carry over automatically, even from a Template — Domino Datasets aren't copied along with it — is the raw data. Do the step below once for your project before running Exercise A.

## Populate the Domino Dataset

This is required, not optional — Exercise A reads the raw transaction data from here, and there's nothing bundled in the code to fall back to.

- [ ] In the project, go to **Data** → confirm the project's default Domino Dataset exists (Domino provisions one automatically for a new project).
- [ ] Upload `raw_cc_transactions.csv.gz` into that Dataset, at its root (not a subfolder). If you received it as `fraud-workshop-data.zip`, upload the zip instead and run `.setup/unzip_dataset.ipynb` once to extract it in place.
- [ ] Confirm it's there before moving on — Exercise A will fail immediately if it isn't.

## Verify everything works

Work through this once, in order — each exercise's output feeds the next.

### 1. Environment sanity check
- [ ] Open a workspace terminal and run `python .setup/verify_environment.py` — it checks every
  package the workshop needs and prints PASS or the missing ones. Or check by hand: `pandas`, `numpy`, `sklearn`, `xgboost`, `mlflow`, `joblib`, `flytekit`, `flytekitplugins.domino`, `domino` (python-domino), `streamlit`. `ydata_profiling` is optional - Exercise B skips its EDA report if it isn't installed.
- [ ] If `ydata_profiling` fails to import with `ModuleNotFoundError: No module named 'pkg_resources'`, your environment was built before the `setuptools<81` pin was added to `environment.md`/`Dockerfile` — update the pip install line to match and rebuild the environment. Confirmed to fix it: newer `setuptools` dropped `pkg_resources`, which `ydata_profiling` still needs (4.18 included).

### 2. Exercise A — Data Exploration
- [ ] Confirm "Populate the Domino Dataset" above is done first.
- [ ] Open the notebook (`exercises/a_DataExploration/data_exploration_notebook.ipynb`) in a Jupyter/JupyterLab workspace and run it top to bottom.
- [ ] Confirm the 5 plots show up under Artifacts, and `clean_cc_transactions.csv` lands alongside the raw file in the project's Domino Dataset.

### 3. Exercise B — Data Engineering
- [ ] Run `exercises/b_DataEngineering/data_engineering.py` as a Job (per the exercise instructions — Click "Run Job" in the UI).
- [ ] Confirm the Job succeeds, `preprocessing_report.html` shows up under Artifacts, a new "CC Fraud Preprocessing ..." run appears in Experiment Manager, and `transformed_cc_transactions.csv` lands in the Dataset.

### 4. Exercise C — Training & Evaluation
- [ ] From a workspace terminal, run the three trainer scripts directly — this is the confirmed-working path:
  ```
  python exercises/c_TrainingAndEvaluation/trainer_ada.py
  python exercises/c_TrainingAndEvaluation/trainer_gnb.py
  python exercises/c_TrainingAndEvaluation/trainer_xgb.py
  ```
  To demo Flows instead, `workflow.py` runs these same three trainers as an orchestrated
  Domino Flow - but it needs one extra setup step first. Flow tasks don't get the project's
  read-write Dataset the way Jobs and Workspaces do; they only see dataset snapshots the task
  attaches. So: **Data -> the project's Dataset -> create a snapshot** (after Exercise B, so it
  captures `transformed_cc_transactions.csv`), then run
  `pyflyte run --remote exercises/c_TrainingAndEvaluation/workflow.py credit_card_fraud_detection_workflow`.
  Once a snapshot exists, Domino attaches it to each Flow task automatically from the
  project defaults - `workflow.py` needs no dataset configuration of its own. Without a
  snapshot the tasks get no dataset mount at all and fail with a `FileNotFoundError`.
- [ ] In Experiment Manager, select all 3 runs and Compare — XGBoost should come out on top on ROC AUC, matching the exercise instructions' own hint.
- [ ] Register the XGBoost run's model to the Model Registry.

### 5. Exercise D — Delivery & Hosting
- [ ] Deploy a Model API endpoint from the registered XGBoost model. Copy its endpoint URL and auth token.
  If the endpoint never starts and the logs show `no app loaded. GAME OVER` with
  `configparser.SafeConfigParser`, the environment was built without the last
  instruction in `.setup/Dockerfile` - that line is what makes endpoints work on
  Python 3.12.
- [ ] Set `xgboost_endpoint` / `xgboost_auth` as environment variables (same pattern for `adaboost_*`/`gaussiannb_*` if you want all three selectable in the UI). Project → Settings → Environment Variables is the most reliable place — those apply project-wide to workspaces, jobs, and apps alike. Some Domino versions also offer a per-App environment variable screen; either works, since `app.py` just reads `os.environ.get(...)` regardless of which layer set it.
- [ ] Publish `app.py` as a Domino App and submit a test transaction with the XGBoost model selected.
- [ ] **Confirm the returned score is a real model prediction, not the fallback heuristic** — the app doesn't error if the endpoint env vars are missing or wrong, it just silently returns a hand-coded 6-flag score instead. If in doubt, temporarily unset the env var and compare the two outputs so you know what the fallback looks like.
- [ ] Optionally set up a Launcher pointing at one of the trainer scripts, per the exercise instructions.
