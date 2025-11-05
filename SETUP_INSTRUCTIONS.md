# CVD Risk Prediction System - Setup Instructions

## Overview
This system connects your web interface to the ML model for cardiovascular disease risk prediction.

**Flow:**
```
Web Form → Firebase (optional) → API Server → ML Model (Black Box) → YES/NO → Web Interface
```

---

## Installation Steps

### 1. Install Required Python Packages

```bash
cd "/Users/nandihawkins/Desktop/Class Notes/NCAT/COMP 496/Cardiovascular_Disease_Prediction_with_Explainable_AI"

pip install flask flask-cors pandas numpy scikit-learn imbalanced-learn openpyxl
```

### 2. Train and Save the ML Model

```bash
python cvd_risk_predictor.py
```

This will create:
- `cvd_model.pkl` - The trained Random Forest model
- `cvd_scaler.pkl` - The data scaler

### 3. Start the API Server

```bash
python api_server.py
```

The server will start at: `http://localhost:5000`

You should see:
```
CVD Risk Prediction API Server
====================================
Endpoints:
  GET  /health           - Health check
  POST /predict          - Predict single patient
  POST /predict-batch    - Predict multiple patients
====================================
```

---

## API Endpoints

### 1. Health Check
```
GET http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 2. Single Patient Prediction
```
POST http://localhost:5000/predict
Content-Type: application/json
```

**Request Body:**
```json
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
```

**Response:**
```json
{
  "cvd_risk": "YES",
  "risk_probability": 0.85,
  "risk_percentage": "85.0%",
  "risk_level": "HIGH RISK",
  "success": true
}
```

### 3. Get Required Fields
```
GET http://localhost:5000/required-fields
```

**Response:**
```json
{
  "required_fields": ["age", "anaemia", ...],
  "descriptions": {
    "age": "Age in years",
    "anaemia": "0 = No, 1 = Yes",
    ...
  }
}
```

---

## JavaScript Integration

### Basic Usage (Standalone)

```javascript
// Make prediction
const patientData = {
  age: 65,
  anaemia: 0,
  creatinine_phosphokinase: 582,
  diabetes: 0,
  ejection_fraction: 20,
  high_blood_pressure: 0,
  platelets: 265000,
  serum_creatinine: 1.9,
  serum_sodium: 130,
  sex: 1,
  smoking: 0,
  time: 4
};

const response = await fetch('http://localhost:5000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(patientData)
});

const result = await response.json();
console.log(result.cvd_risk);  // "YES" or "NO"
```

### With Firebase

See `example_frontend_integration.js` for complete example with Firebase integration.

**Steps:**
1. Collect patient data from your web form
2. (Optional) Store in Firebase
3. Send to API for prediction
4. Display YES/NO result
5. (Optional) Save prediction result to Firebase

---

## Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| age | number | Age in years | 65 |
| anaemia | 0 or 1 | Has anemia? | 0 = No, 1 = Yes |
| creatinine_phosphokinase | number | CPK enzyme level (mcg/L) | 582 |
| diabetes | 0 or 1 | Has diabetes? | 0 = No, 1 = Yes |
| ejection_fraction | number | Blood ejection % | 20 |
| high_blood_pressure | 0 or 1 | Has high BP? | 0 = No, 1 = Yes |
| platelets | number | Platelet count (kiloplatelets/mL) | 265000 |
| serum_creatinine | number | Serum creatinine (mg/dL) | 1.9 |
| serum_sodium | number | Serum sodium (mEq/L) | 130 |
| sex | 0 or 1 | Gender | 0 = Female, 1 = Male |
| smoking | 0 or 1 | Smokes? | 0 = No, 1 = Yes |
| time | number | Follow-up period (days) | 4 |

---

## Testing the API

### Using curl:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Using Python:

```python
import requests

patient = {
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

response = requests.post('http://localhost:5000/predict', json=patient)
print(response.json())
```

---

## Deployment Considerations

### For Production:

1. **Change `debug=False`** in `api_server.py`
2. **Use a production server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
   ```
3. **Update CORS settings** to allow only your domain
4. **Use HTTPS** for secure communication
5. **Deploy to cloud** (AWS, Google Cloud, Heroku, etc.)
6. **Update API_BASE_URL** in your JavaScript to production URL

### Environment Variables (Optional):

Create a `.env` file:
```
FLASK_ENV=production
API_PORT=5000
MODEL_PATH=cvd_model.pkl
SCALER_PATH=cvd_scaler.pkl
```

---

## Troubleshooting

### "Model files not found"
- Run `python cvd_risk_predictor.py` first to train the model

### "CORS error" in browser
- Flask-CORS is installed and enabled in `api_server.py`
- Check browser console for specific error

### "Connection refused"
- Ensure API server is running: `python api_server.py`
- Check firewall settings

### "Missing required field" error
- Verify all 12 fields are included in the request
- Check field names match exactly (case-sensitive)

---

## Complete Firebase Integration (Web Interface)

### Files for Web Integration

Located in `/Users/nandihawkins/Downloads/`:

1. **app_cvd_integrated.js** - Complete JavaScript with Firebase + ML API integration
2. **cvd_assessment_form.html** - Example HTML form with all required fields
3. **INTEGRATION_GUIDE.md** - Detailed web integration instructions

### Quick Web Integration Setup

1. **Ensure API server is running:**
   ```bash
   python api_server.py
   ```

2. **Use the integrated JavaScript:**
   - Replace your `app.js` with `app_cvd_integrated.js`
   - Already includes your Firebase config
   - Handles form submission → ML prediction → Firebase storage

3. **Update your HTML form to include these field IDs:**
   ```html
   <input type="number" id="age">
   <select id="anaemia">
   <input type="number" id="creatinine_phosphokinase">
   <select id="diabetes">
   <input type="number" id="ejection_fraction">
   <select id="high_blood_pressure">
   <input type="number" id="platelets">
   <input type="number" id="serum_creatinine">
   <input type="number" id="serum_sodium">
   <select id="sex">
   <select id="smoking">
   <input type="number" id="time">
   <div id="predictionResult"></div>
   ```

4. **What happens automatically:**
   - User fills form
   - Data sent to ML API
   - YES/NO prediction displayed
   - All data + prediction saved to Firebase `cvd_assessments` collection

### Firebase Data Structure

Each submission creates a document in the `cvd_assessments` collection:

```javascript
{
  patientName: "Optional name",
  patientData: {
    age: 65,
    anaemia: 0,
    creatinine_phosphokinase: 582,
    diabetes: 0,
    ejection_fraction: 20,
    high_blood_pressure: 0,
    platelets: 265000,
    serum_creatinine: 1.9,
    serum_sodium: 130,
    sex: 1,
    smoking: 0,
    time: 4
  },
  prediction: {
    cvd_risk: "YES",           // ← YES/NO answer
    risk_probability: 0.85,
    risk_percentage: "85.0%",
    risk_level: "HIGH RISK"
  },
  timestamp: Timestamp
}
```

---

## Next Steps

1. ✅ Test the API with sample data (see Testing section above)
2. ✅ Integrate with your web form using provided JavaScript
3. Deploy to production environment
4. Set up Firebase security rules for production

---

## Support

For issues or questions, check:
- **Web Integration:** `/Users/nandihawkins/Downloads/INTEGRATION_GUIDE.md`
- **API Details:** `api_server.py`
- **ML Model:** `cvd_risk_predictor.py`
- **JavaScript Example:** `example_frontend_integration.js`
- **Complete HTML Form:** `/Users/nandihawkins/Downloads/cvd_assessment_form.html`
