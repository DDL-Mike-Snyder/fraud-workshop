# Training And Evaluation
In this phase, we will train 3 models, evaluate them, and register the best one.  We will run the three training scripts, compare them in the Domino Experiment Manager, and register the winner in the Model Registry.

`workflow.py` can run the same three trainers as an orchestrated Domino Flow instead.  That needs one extra step first - a snapshot of the project's Dataset, because Flow tasks only see dataset snapshots rather than the project's read-write Dataset.  See `.setup/SETUP.md`.

## Exercise Instructions

In the workspace, open the terminal

Run the three trainer programs:

```
python exercises/c_TrainingAndEvaluation/trainer_ada.py
python exercises/c_TrainingAndEvaluation/trainer_gnb.py
python exercises/c_TrainingAndEvaluation/trainer_xgb.py
```

Click "Experiment Manager"  (Main Window, Left-Hand Column)

Select all runs (3) and click "Compare"

Select the one with the best metrics (here is a hint: XGBoost)

Review the complete traceability and all factors.

Click "Register Model From Run" in Upper Right Hand

Create model name

This concludes the "3. MODEL TRAINING and EVALUATION" section of the workshop.

## New Domino Concepts

**Experiment Manager:**
> Experiment Manager is a centralized tracking system that automatically captures and compares all experiment runs, including parameters, metrics, code versions, and results in a searchable interface. This accelerates model development by enabling data scientists to quickly identify the best-performing models, understand what changes improved performance, and reproduce any past experiment.

**Model Registry:**
> Model Registry is a centralized repository that catalogs all trained models with their metadata, performance metrics, lineage, and deployment status throughout their lifecycle. This provides governance and collaboration capabilities by enabling teams to discover, compare, promote, and deploy models while maintaining full auditability and compliance documentation.
