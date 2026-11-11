# Fraud-Detection-Workshop
This workshop gives attendees hands-on experience with the Domino Data Lab platform by working through the complete model development and delivery lifecycle, from data preparation to model delivery.

## Setup
Before starting, the raw transaction data must be in the project's Domino Dataset — see `.setup/SETUP.md`. The compute environment spec is in `.setup/environment.md`.

## Exercises
Each exercise directory contains the instructions, notebooks, and scripts needed to complete it. Each builds on the previous one, so they must be completed in order.

### 1 - Data Exploration
Interactive notebook. Reads the raw transaction data from the project's Domino Dataset into a dataframe, removes dirty data, generates plots, and saves the cleaned data back to the Dataset.

### 2 - Data Engineering
Python script executed as a Domino Job. Reads the cleaned data from the Domino Dataset, adds derived columns, normalizes/scales/encodes the features, saves the result to the Dataset, and logs the preprocessing pipeline plus an EDA report to the Experiment Manager.

### 3 - Model Training & Evaluation
Three training scripts (AdaBoost, GaussianNB, XGBoost) run from a workspace terminal, each logging metrics, plots, and its model to the Experiment Manager. Compare the runs, then register the best model to the Model Registry.

An optional Domino Flow (`workflow.py`) runs the same three trainers as orchestrated job tasks and compares the results.

### 4 - Delivery & Hosting
- Hosted REST API endpoints
- Hosted web apps
- Launchers

### Optional Add-On - Agent Investigation
A small LLM agent that investigates a flagged transaction using two mock lookup tools and returns a recommendation, traced end to end with Domino's GenAI tracing. Requires the `anthropic` package and an `ANTHROPIC_API_KEY`, so it is not part of the core exercise flow — see `exercises/e_AgentAddOn/`.
