"""
Credit Card Fraud Detection Preprocessing Pipeline

This script performs data preprocessing for credit card fraud detection:
1. Loads cleaned transaction data from a CSV file
2. Creates derived features to enhance fraud detection capabilities
3. Applies preprocessing transformations (scaling numerical features, encoding categorical features)
4. Generates an EDA (Exploratory Data Analysis) report
5. Saves the transformed features and logs everything to MLflow

The pipeline is designed to work within the Domino Data Lab platform and uses
MLflow for experiment tracking and model logging.
"""

import os, time
from datetime import datetime
import pandas as pd
import numpy as np
import mlflow
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from mlflow.models import infer_signature
import sys
sys.path.append(os.environ["DOMINO_WORKING_DIR"])
from domino_short_id import domino_short_id


# Configure experiment name with a unique identifier to avoid conflicts
experiment_name = f"CC Fraud Preprocessing {domino_short_id()}"

# Define filenames for input and output data
clean_filename = 'clean_cc_transactions.csv'  # Input: cleaned transaction data
features_filename = 'transformed_cc_transactions.csv'  # Output: preprocessed features

# Get Domino environment paths (defaults provided for local development)
domino_project_name = os.environ.get("DOMINO_PROJECT_NAME", "my-local-project")

domino_username = os.environ.get("DOMINO_USER_NAME")
is_git_based_project = os.environ.get("DOMINO_IS_GIT_BASED")

# Construct paths for data storage and artifacts
# In Domino, 'data' directory is for datasets, 'artifacts' for outputs like reports
domino_data_dir = os.environ.get("DOMINO_DATASETS_DIR","/domino/datasets/")
if is_git_based_project == "true":
    domino_dataset_dir = f"{domino_data_dir}/{domino_project_name}/{domino_username}"
else:
    domino_dataset_dir = f"{domino_data_dir}/local/{domino_project_name}"
# DFS Projects have no separate artifacts store - they're just files in the working dir.
if is_git_based_project == "true":
    domino_artifact_dir = os.path.join(os.environ.get("DOMINO_ARTIFACTS_DIR", "/mnt/artifacts"), "b_data_engineering")
else:
    domino_artifact_dir = f"{os.environ.get('DOMINO_WORKING_DIR', '/mnt')}/artifacts/b_data_engineering"
os.makedirs(domino_artifact_dir, exist_ok=True)
clean_path = f"{domino_dataset_dir}/{clean_filename}"


def get_generation_label(age):
   birth_year = datetime.today().year - age
   
   if birth_year <= 1945:
       return "Silent Generation"
   elif birth_year <= 1964:
       return "Baby Boomer"
   elif birth_year <= 1980:
       return "Generation X"
   elif birth_year <= 1996:
       return "Millennial"
   elif birth_year <= 2012:
       return "Generation Z"
   else:
       return "Generation Alpha"


def add_derived_features(df):
    """
    Create derived features to enhance fraud detection capabilities.
    
    This function engineers new features based on domain knowledge and
    patterns commonly associated with fraudulent transactions.
    
    Args:
        df (pd.DataFrame): Input dataframe with original transaction features
        
    Returns:
        pd.DataFrame: Dataframe with additional derived features
        
    Derived Features:
        - amount_vs_avg30d_ratio: Ratio of current transaction amount to 30-day average
          (helps detect unusual spending patterns)
        - risk_score: Combined merchant and IP reputation risk (0-1 scale)
        - trust_score: Device trust minus merchant risk (indicates device-merchant mismatch)
        - generation: Customer generation based on age (e.g., Millennial, Gen X)
    """
    # Velocity features: Compare current transaction to historical spending
    # Adding small epsilon (1e-6) to avoid division by zero
    df['amount_vs_avg30d_ratio'] = df['Amount'] / (df['Avg30d'] + 1e-6)

    # Risk composite scores: Combine multiple risk indicators
    # Average of merchant risk and IP reputation (both on 0-1 scale)
    df['risk_score'] = (df['MerchantRisk'] + df['IPReputation']) / 2
    
    # Trust score: Positive values indicate trusted device on risky merchant
    # Negative values indicate untrusted device on safe merchant
    df['trust_score'] = df['DeviceTrust'] - df['MerchantRisk']
    
    # Age-based generation label (uses helper function to categorize)
    df['generation'] = df['Age'].apply(get_generation_label)
    
    return df




if __name__ == "__main__":
        
    # Set up MLflow experiment for tracking
    mlflow.set_experiment(experiment_name)
    
    # Start MLflow run to track this preprocessing execution
    with mlflow.start_run(run_name="Preprocessing Pipeline") as run:
        # Step 1: Load the cleaned transaction dataset
        print(f"Loading clean dataset from {clean_path}")
        clean_df = pd.read_csv(clean_path, index_col=0)
        print(f"Loaded {len(clean_df):,} rows from {clean_path}")
        print(clean_df.columns)
        
        # Step 2: Generate derived features for enhanced fraud detection
        full_cleaned_df = add_derived_features(clean_df)
        
        # Step 3: Separate target variable (Class) from features
        # Class: 0 = legitimate transaction, 1 = fraudulent transaction
        labels_df = full_cleaned_df['Class']
        features_df = full_cleaned_df.drop(columns=['Class'], errors='ignore')
        
        # Identify feature types for appropriate preprocessing
        numeric_features = features_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_features = features_df.select_dtypes(include=[object,
                                                                    "category"]).columns.tolist()
        print(features_df)
        
        # Step 4: Create preprocessing pipeline
        # Numeric features: StandardScaler (mean=0, std=1)
        # Categorical features: One-hot encoding with unknown category handling
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
                 categorical_features)
            ]
        )
        pipeline = Pipeline([("preproc", preprocessor)])
        
        # Fit and transform the features, tracking execution time
        start_time = time.time()
        transformed_features_array = pipeline.fit_transform(features_df)
        fit_time = time.time() - start_time
        print(f"Transformed features in {fit_time:.2} seconds.")
    
        # Step 5: Convert transformed array back to DataFrame with proper column names
        # This preserves feature interpretability after one-hot encoding
        feature_names = pipeline.named_steps['preproc'].get_feature_names_out()
        transformed_features_df = pd.DataFrame(transformed_features_array,
                                               columns=feature_names, index=features_df.index)
    
        # Add labels back to the transformed features
        transformed_features_df['Class'] = labels_df
        
        # Step 6: Save transformed features for model training
        features_path = f"{domino_dataset_dir}/{features_filename}"
        transformed_features_df.to_csv(features_path, index=False)
        print('saved to ', f"{domino_dataset_dir}/{features_filename}")
    
        # Step 7: Generate comprehensive EDA report using ydata-profiling
        # Save EDA report as HTML in artifacts directory
        eda_path = f"{domino_artifact_dir}/preprocessing_report.html"
        try:
            from ydata_profiling import ProfileReport  # imported here b/c importing outside main slows down other references.
            profile = ProfileReport(
                clean_df, 
                title="Credit Card Fraud Detection - EDA Report",
                explorative=True,
                minimal=True
            )
            profile.to_file(eda_path)
        except ImportError:
            # Optional dependency - the rest of the exercise doesn't need it.
            eda_path = None
            print("ydata-profiling not installed - skipping the EDA report.")
    
        # Step 8: Log all artifacts and metrics to MLflow for tracking
        # Log input data reference
        mlflow.log_artifact(clean_path, artifact_path="data")
        
        # Log EDA report
        if eda_path:
            mlflow.log_artifact(eda_path, artifact_path="eda")
        
        # Log preprocessing statistics
        mlflow.log_param("num_rows_loaded", len(features_df))
        mlflow.log_param("num_cat_features", len(categorical_features))
        mlflow.log_param("num_num_features", len(numeric_features))
        mlflow.log_metric("fit_time", fit_time)
    
        # Step 9: Prepare pipeline for MLflow model logging
        # Add predict method alias for compatibility with MLflow's sklearn flavor
        pipeline.predict = pipeline.transform
        
        # Create sample data for model signature inference
        # Using first 20 rows as representative sample
        X_sample = features_df.iloc[:20].copy()
        
        # Ensure numeric features are float64 for signature compatibility
        for col in numeric_features:
            if np.issubdtype(X_sample[col].dtype, np.integer):
                X_sample[col] = X_sample[col].astype("float64")
        
        # Generate signature by transforming sample data
        y_sample = pipeline.transform(X_sample)
        signature = infer_signature(X_sample, y_sample)
        
        # Log the preprocessing pipeline as an MLflow model
        # This allows the pipeline to be loaded and used in downstream processes
        mlflow.sklearn.log_model(
            pipeline,
            artifact_path="preprocessing_pipeline",
            # registered_model_name="CC Fraud Preprocessing",  # Uncomment to auto-register as Domino model
            signature=signature
        )
        
        # Tag this run as a preprocessing pipeline for easy filtering
        mlflow.set_tag("pipeline", "preprocessing")
        
