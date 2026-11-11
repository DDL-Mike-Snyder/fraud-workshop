import os
from domino import Domino
project = os.environ['DOMINO_PROJECT_NAME']
user = os.environ['DOMINO_PROJECT_OWNER']
domino = Domino(
    f"{user}/{project}",
    api_key = os.environ["DOMINO_USER_API_KEY"],
    host = os.environ["DOMINO_API_HOST"],
)
hwtier = 'Medium'
execution = 'exercises/c_TrainingAndEvaluation/trainer_xgb.py'
title = f'Train XGBoost classifier'
domino.job_start(execution, title=title, hardware_tier_name=hwtier)
