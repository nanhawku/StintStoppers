"""
Cardiovascular Disease Risk Predictor
Reads patient data from Excel and predicts CVD risk (YES/NO)
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class CVDRiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'age', 'anaemia', 'creatinine_phosphokinase', 'diabetes',
            'ejection_fraction', 'high_blood_pressure', 'platelets',
            'serum_creatinine', 'serum_sodium', 'sex', 'smoking', 'time'
        ]
        self.continuous_vars = [
            'age', 'creatinine_phosphokinase', 'ejection_fraction',
            'platelets', 'serum_creatinine', 'serum_sodium', 'time'
        ]

    def train_model(self, training_data_path):
        """Train the model using the heart failure dataset"""
        print("Loading training data...")
        df = pd.read_csv(training_data_path)

        # Remove duplicates
        df = df.drop_duplicates()

        # Normalize continuous variables
        self.scaler = StandardScaler()
        df[self.continuous_vars] = self.scaler.fit_transform(df[self.continuous_vars])

        # Define features and target
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values

        # Check class distribution before SMOTE
        counter_before = Counter(y)
        print(f'Class distribution before SMOTE: {counter_before}')

        # Apply SMOTE to balance classes
        oversample = SMOTE(random_state=42)
        X, y = oversample.fit_resample(X, y)

        # Check class distribution after SMOTE
        counter_after = Counter(y)
        print(f'Class distribution after SMOTE: {counter_after}')

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.30, random_state=42
        )

        # Train Random Forest model (best performing model from notebook)
        print("\nTraining Random Forest model...")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f'\nModel Performance:')
        print(f'Accuracy: {accuracy:.2%}')
        print(f'Precision: {precision:.2%}')
        print(f'Recall: {recall:.2%}')
        print(f'F1 Score: {f1:.2%}')

        return self

    def save_model(self, model_path='cvd_model.pkl', scaler_path='cvd_scaler.pkl'):
        """Save the trained model and scaler"""
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"\nModel saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")

    def load_model(self, model_path='cvd_model.pkl', scaler_path='cvd_scaler.pkl'):
        """Load a pre-trained model and scaler"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        print("Model and scaler loaded successfully")
        return self

    def predict_from_excel(self, excel_path, output_path=None):
        """
        Read patient data from Excel and predict CVD risk

        Expected columns in Excel:
        - age: Age of patient
        - anaemia: 0 or 1
        - creatinine_phosphokinase: CPK enzyme level
        - diabetes: 0 or 1
        - ejection_fraction: Percentage of blood leaving heart
        - high_blood_pressure: 0 or 1
        - platelets: Platelet count
        - serum_creatinine: Serum creatinine level
        - serum_sodium: Serum sodium level
        - sex: 0 (female) or 1 (male)
        - smoking: 0 or 1
        - time: Follow-up period (days)
        """
        print(f"\nReading patient data from {excel_path}...")

        # Read Excel file
        df = pd.read_excel(excel_path)

        print(f"Loaded {len(df)} patient records")

        # Check if all required columns are present
        missing_cols = [col for col in self.feature_names if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Reorder columns to match training data
        df_features = df[self.feature_names].copy()

        # Store original data for output
        df_output = df.copy()

        # Normalize continuous variables using the saved scaler
        df_features[self.continuous_vars] = self.scaler.transform(
            df_features[self.continuous_vars]
        )

        # Make predictions
        print("Making predictions...")
        predictions = self.model.predict(df_features.values)
        probabilities = self.model.predict_proba(df_features.values)[:, 1]

        # Convert to YES/NO
        risk_assessment = ['YES' if pred == 1 else 'NO' for pred in predictions]

        # Add results to output dataframe
        df_output['CVD_RISK'] = risk_assessment
        df_output['RISK_PROBABILITY'] = [f"{prob:.1%}" for prob in probabilities]
        df_output['RISK_LEVEL'] = df_output['CVD_RISK'].apply(
            lambda x: 'HIGH RISK' if x == 'YES' else 'LOW RISK'
        )

        # Print summary
        yes_count = sum(1 for x in risk_assessment if x == 'YES')
        no_count = len(risk_assessment) - yes_count

        print(f"\n{'='*60}")
        print(f"PREDICTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total patients assessed: {len(df_output)}")
        print(f"HIGH RISK (YES): {yes_count} ({yes_count/len(df_output)*100:.1f}%)")
        print(f"LOW RISK (NO): {no_count} ({no_count/len(df_output)*100:.1f}%)")
        print(f"{'='*60}\n")

        # Save results if output path provided
        if output_path:
            df_output.to_excel(output_path, index=False)
            print(f"Results saved to {output_path}")

        return df_output


def main():
    """Main function to demonstrate usage"""
    import os

    # Initialize predictor
    predictor = CVDRiskPredictor()

    # Path to training data
    training_data = '/Users/nandihawkins/Desktop/Class Notes/NCAT/COMP 496/Cardiovascular_Disease_Prediction_with_Explainable_AI/heart_failure.csv'

    # Check if model already exists
    if os.path.exists('cvd_model.pkl') and os.path.exists('cvd_scaler.pkl'):
        print("Loading existing model...")
        predictor.load_model()
    else:
        print("No existing model found. Training new model...")
        predictor.train_model(training_data)
        predictor.save_model()

    # Example: Process patient data
    # Replace 'patient_data.xlsx' with your actual Excel file path
    print("\n" + "="*60)
    print("Ready to process patient data!")
    print("="*60)
    print("\nUsage:")
    print("  predictor.predict_from_excel('patient_data.xlsx', 'results.xlsx')")
    print("\nRequired Excel columns:")
    for feature in predictor.feature_names:
        print(f"  - {feature}")

    return predictor


if __name__ == "__main__":
    predictor = main()
