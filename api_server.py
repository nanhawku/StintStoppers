"""
Flask API Server for CVD Risk Prediction
Receives patient data from web interface and returns YES/NO prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for web requests

# Global variables for model and scaler
model = None
scaler = None
feature_names = [
    'age', 'anaemia', 'creatinine_phosphokinase', 'diabetes',
    'ejection_fraction', 'high_blood_pressure', 'platelets',
    'serum_creatinine', 'serum_sodium', 'sex', 'smoking', 'time'
]
continuous_vars = [
    'age', 'creatinine_phosphokinase', 'ejection_fraction',
    'platelets', 'serum_creatinine', 'serum_sodium', 'time'
]


def load_model():
    """Load the trained model and scaler"""
    global model, scaler

    model_path = 'cvd_model.pkl'
    scaler_path = 'cvd_scaler.pkl'

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError(
            "Model files not found. Please run cvd_risk_predictor.py first to train the model."
        )

    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)

    print("Model and scaler loaded successfully")


def preprocess_patient_data(patient_data):
    """
    Preprocess patient data for prediction

    Parameters:
    -----------
    patient_data : dict
        Dictionary containing patient features

    Returns:
    --------
    numpy array ready for prediction
    """
    # Extract features in correct order
    features = []
    for feature in feature_names:
        if feature not in patient_data:
            raise ValueError(f"Missing required field: {feature}")
        features.append(float(patient_data[feature]))

    # Convert to numpy array
    features_array = np.array(features).reshape(1, -1)

    # Create a copy for scaling
    scaled_features = features_array.copy()

    # Get indices of continuous variables
    continuous_indices = [feature_names.index(var) for var in continuous_vars]

    # Scale only continuous variables
    scaled_features[0, continuous_indices] = scaler.transform(
        features_array[:, continuous_indices]
    )[0]

    return scaled_features


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint

    Expects JSON with patient data:
    {
        "age": 65,
        "anaemia": 0,
        "creatinine_phosphokinase": 582,
        "diabetes": 0,
        "ejection_fraction": 20,
        "high_blood_pressure": 0,
        "platelets": 265000,
        "serum_creatinine": 1.9,
        "serum_sodium": 130,
        "sex": 1,
        "smoking": 0,
        "time": 4
    }

    Returns:
    {
        "cvd_risk": "YES" or "NO",
        "risk_probability": 0.85,
        "risk_level": "HIGH RISK" or "LOW RISK"
    }
    """
    try:
        # Get patient data from request
        patient_data = request.json

        if not patient_data:
            return jsonify({
                'error': 'No data provided'
            }), 400

        # Preprocess data
        features = preprocess_patient_data(patient_data)

        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0, 1]

        # Convert to YES/NO
        cvd_risk = "YES" if prediction == 1 else "NO"
        risk_level = "HIGH RISK" if prediction == 1 else "LOW RISK"

        # Return result
        return jsonify({
            'cvd_risk': cvd_risk,
            'risk_probability': float(probability),
            'risk_percentage': f"{probability * 100:.1f}%",
            'risk_level': risk_level,
            'success': True
        })

    except ValueError as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 400

    except Exception as e:
        return jsonify({
            'error': f'Prediction failed: {str(e)}',
            'success': False
        }), 500


@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint for multiple patients

    Expects JSON with array of patient data:
    {
        "patients": [
            { patient_data_1 },
            { patient_data_2 },
            ...
        ]
    }

    Returns:
    {
        "results": [
            { prediction_1 },
            { prediction_2 },
            ...
        ]
    }
    """
    try:
        data = request.json

        if not data or 'patients' not in data:
            return jsonify({
                'error': 'No patient data provided'
            }), 400

        patients = data['patients']
        results = []

        for i, patient_data in enumerate(patients):
            try:
                # Preprocess data
                features = preprocess_patient_data(patient_data)

                # Make prediction
                prediction = model.predict(features)[0]
                probability = model.predict_proba(features)[0, 1]

                # Convert to YES/NO
                cvd_risk = "YES" if prediction == 1 else "NO"
                risk_level = "HIGH RISK" if prediction == 1 else "LOW RISK"

                results.append({
                    'patient_index': i,
                    'cvd_risk': cvd_risk,
                    'risk_probability': float(probability),
                    'risk_percentage': f"{probability * 100:.1f}%",
                    'risk_level': risk_level,
                    'success': True
                })

            except Exception as e:
                results.append({
                    'patient_index': i,
                    'error': str(e),
                    'success': False
                })

        return jsonify({
            'results': results,
            'total': len(patients),
            'successful': sum(1 for r in results if r.get('success', False))
        })

    except Exception as e:
        return jsonify({
            'error': f'Batch prediction failed: {str(e)}',
            'success': False
        }), 500


@app.route('/required-fields', methods=['GET'])
def get_required_fields():
    """Return list of required fields and their descriptions"""
    field_descriptions = {
        'age': 'Age in years',
        'anaemia': '0 = No, 1 = Yes',
        'creatinine_phosphokinase': 'CPK enzyme level (mcg/L)',
        'diabetes': '0 = No, 1 = Yes',
        'ejection_fraction': 'Percentage of blood leaving heart (%)',
        'high_blood_pressure': '0 = No, 1 = Yes',
        'platelets': 'Platelet count (kiloplatelets/mL)',
        'serum_creatinine': 'Serum creatinine level (mg/dL)',
        'serum_sodium': 'Serum sodium level (mEq/L)',
        'sex': '0 = Female, 1 = Male',
        'smoking': '0 = No, 1 = Yes',
        'time': 'Follow-up period (days)'
    }

    return jsonify({
        'required_fields': feature_names,
        'descriptions': field_descriptions
    })


if __name__ == '__main__':
    # Load model on startup
    print("Loading ML model...")
    load_model()
    print("Model loaded successfully!")

    # Start server
    print("\n" + "="*60)
    print("CVD Risk Prediction API Server")
    print("="*60)
    print("Endpoints:")
    print("  GET  /health           - Health check")
    print("  GET  /required-fields  - Get required field information")
    print("  POST /predict          - Predict single patient")
    print("  POST /predict-batch    - Predict multiple patients")
    print("="*60)
    print("\nServer starting on http://localhost:5000")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
