# Data Exploration
In this phase, we will begin the process of exploring a transactional dataset to see if it will be good for model training.  We will read a CSV file from a Domino Dataset into a Dataframe, clean the data, generate some visualizations, and save the cleaned data back to that Domino Dataset.  We will begin from within your copy of the "Fraud Detection Workshop" project.

**Prerequisite:** the raw `raw_cc_transactions.csv.gz` file must already be in this project's Domino Dataset before this exercise will run — see `.setup/SETUP.md`, "Populate the Domino Dataset." This is a one-time setup step per project.

## Exercise Instructions

1.  Click "Workspace" (Left-hand column) and click "Jupyter Lab"

2.  Click "Next" 4x and then "Create"
    - Feel free to look around but do not change anything.

3.  Review Workspace Creation Workflow

4.  Review Workspace UI & Lefthand Sidebar

5.  Open the notebook `exercises/a_DataExploration/data_exploration_notebook.ipynb`

6.  Run notebook cells (either manually or automatically)

7.  Review generated MetaData and Plots

8.  Review the generated plots under `artifacts/a_data_exploration/`

9.  Confirm `clean_cc_transactions.csv` now sits alongside the raw file in the project's Domino Dataset

10. Save and Commit Code

This concludes the "1. Data Exploration" section of the workshop

## New Domino Concepts
**Workspaces:** 
> A Domino workspace is an interactive session where you can conduct research, analyze data, train models, and more. Use workspaces to work in the development environment of your choice, like Jupyter notebooks, RStudio, VS Code, and many other customizable environments.

**Domino Dataset:**
> A Domino Dataset is a versioned, centralized data repository that enables teams to share, track, and manage data assets across projects and experiments. This ensures data consistency and reproducibility while providing governance controls and lineage tracking, eliminating the need for data scientists to manage their own copies of data.

**Compute Environments:**
> Compute Environments are pre-configured, containerized environments that package all the tools, libraries, and dependencies needed for data science work. They enable instant reproducibility and portability of work across teams while eliminating environment setup overhead and "it works on my machine" issues.

**Hardware Tiers:**
> Hardware Tiers are predefined compute resource configurations (CPU, GPU, memory) that users can select based on their workload requirements. This allows organizations to optimize costs by right-sizing resources for each task while giving data scientists flexibility to scale up for intensive computations without IT intervention.
