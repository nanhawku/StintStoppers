"""
Simple script to run CVD risk predictions on patient data
"""

from cvd_risk_predictor import CVDRiskPredictor

def predict_cvd_risk(input_excel, output_excel=None):
    """
    Predict cardiovascular disease risk from patient Excel file

    Parameters:
    -----------
    input_excel : str
        Path to Excel file with patient data
    output_excel : str, optional
        Path to save results. If None, creates filename with '_results' suffix

    Returns:
    --------
    DataFrame with predictions
    """
    # Initialize predictor
    predictor = CVDRiskPredictor()

    # Load the trained model
    try:
        predictor.load_model('cvd_model.pkl', 'cvd_scaler.pkl')
    except FileNotFoundError:
        print("Model not found. Training new model...")
        training_data = 'heart_failure.csv'
        predictor.train_model(training_data)
        predictor.save_model()

    # Generate output filename if not provided
    if output_excel is None:
        output_excel = input_excel.replace('.xlsx', '_results.xlsx')

    # Make predictions
    results = predictor.predict_from_excel(input_excel, output_excel)

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_prediction.py <input_excel> [output_excel]")
        print("\nExample:")
        print("  python run_prediction.py patient_data.xlsx")
        print("  python run_prediction.py patient_data.xlsx results.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Run prediction
    results = predict_cvd_risk(input_file, output_file)

    # Display results
    print("\nPrediction Results:")
    print("="*80)
    if 'patient_id' in results.columns:
        display_cols = ['patient_id', 'age', 'ejection_fraction', 'serum_creatinine',
                       'CVD_RISK', 'RISK_PROBABILITY', 'RISK_LEVEL']
    else:
        display_cols = ['age', 'ejection_fraction', 'serum_creatinine',
                       'CVD_RISK', 'RISK_PROBABILITY', 'RISK_LEVEL']

    # Filter to only include columns that exist
    display_cols = [col for col in display_cols if col in results.columns]
    print(results[display_cols].to_string(index=False))
    print("="*80)
