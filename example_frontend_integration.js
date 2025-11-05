/**
 * Example JavaScript code for connecting to CVD Risk Prediction API
 * Integrate this with your Firebase web application
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000';  // Change to your deployed API URL

/**
 * Predict CVD risk for a single patient
 *
 * @param {Object} patientData - Patient information from form/Firebase
 * @returns {Promise<Object>} - Prediction result
 */
async function predictCVDRisk(patientData) {
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(patientData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result;

    } catch (error) {
        console.error('Prediction error:', error);
        throw error;
    }
}

/**
 * Example: Get patient data from Firebase and make prediction
 */
async function assessPatientFromFirebase(userId) {
    try {
        // 1. Get patient data from Firebase
        // Replace with your actual Firebase code
        const patientData = await getPatientDataFromFirebase(userId);

        // 2. Make prediction
        const prediction = await predictCVDRisk(patientData);

        // 3. Display result to user
        displayPredictionResult(prediction);

        // 4. Optionally save result back to Firebase
        await savePredictionToFirebase(userId, prediction);

        return prediction;

    } catch (error) {
        console.error('Assessment error:', error);
        handleError(error);
    }
}

/**
 * Example: Get patient data from Firebase Firestore
 * REPLACE THIS with your actual Firebase implementation
 */
async function getPatientDataFromFirebase(userId) {
    // Example using Firebase Firestore
    // Uncomment and modify based on your Firebase setup

    /*
    const db = firebase.firestore();
    const patientDoc = await db.collection('patients').doc(userId).get();

    if (!patientDoc.exists) {
        throw new Error('Patient not found');
    }

    const data = patientDoc.data();
    */

    // Return patient data in the format expected by the API
    return {
        age: 65,                           // from Firebase
        anaemia: 0,                        // 0 or 1
        creatinine_phosphokinase: 582,     // CPK level
        diabetes: 0,                       // 0 or 1
        ejection_fraction: 20,             // percentage
        high_blood_pressure: 0,            // 0 or 1
        platelets: 265000,                 // platelet count
        serum_creatinine: 1.9,             // level
        serum_sodium: 130,                 // level
        sex: 1,                            // 0=female, 1=male
        smoking: 0,                        // 0 or 1
        time: 4                            // follow-up period in days
    };
}

/**
 * Display prediction result to user
 */
function displayPredictionResult(prediction) {
    if (!prediction.success) {
        console.error('Prediction failed:', prediction.error);
        // Show error to user
        alert(`Prediction failed: ${prediction.error}`);
        return;
    }

    // Display result
    const riskStatus = prediction.cvd_risk;  // "YES" or "NO"
    const probability = prediction.risk_percentage;  // e.g., "85.3%"
    const riskLevel = prediction.risk_level;  // "HIGH RISK" or "LOW RISK"

    console.log('CVD Risk Assessment:');
    console.log(`  Risk: ${riskStatus}`);
    console.log(`  Probability: ${probability}`);
    console.log(`  Level: ${riskLevel}`);

    // Update UI (example)
    document.getElementById('cvd-risk').textContent = riskStatus;
    document.getElementById('risk-probability').textContent = probability;
    document.getElementById('risk-level').textContent = riskLevel;

    // Apply styling based on risk
    const resultElement = document.getElementById('result-container');
    if (riskStatus === 'YES') {
        resultElement.classList.add('high-risk');
        resultElement.classList.remove('low-risk');
    } else {
        resultElement.classList.add('low-risk');
        resultElement.classList.remove('high-risk');
    }
}

/**
 * Save prediction result back to Firebase
 */
async function savePredictionToFirebase(userId, prediction) {
    // Example using Firebase Firestore
    // Uncomment and modify based on your Firebase setup

    /*
    const db = firebase.firestore();

    await db.collection('patients').doc(userId).update({
        lastAssessment: {
            cvd_risk: prediction.cvd_risk,
            risk_probability: prediction.risk_probability,
            risk_level: prediction.risk_level,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        }
    });

    // Or save to separate assessments collection
    await db.collection('assessments').add({
        userId: userId,
        cvd_risk: prediction.cvd_risk,
        risk_probability: prediction.risk_probability,
        risk_level: prediction.risk_level,
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
    });
    */

    console.log('Prediction saved to Firebase');
}

/**
 * Handle form submission from web interface
 */
function setupFormHandler() {
    const form = document.getElementById('patient-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Analyzing...';

        try {
            // Gather form data
            const patientData = {
                age: parseFloat(form.age.value),
                anaemia: parseInt(form.anaemia.value),
                creatinine_phosphokinase: parseFloat(form.creatinine_phosphokinase.value),
                diabetes: parseInt(form.diabetes.value),
                ejection_fraction: parseFloat(form.ejection_fraction.value),
                high_blood_pressure: parseInt(form.high_blood_pressure.value),
                platelets: parseFloat(form.platelets.value),
                serum_creatinine: parseFloat(form.serum_creatinine.value),
                serum_sodium: parseFloat(form.serum_sodium.value),
                sex: parseInt(form.sex.value),
                smoking: parseInt(form.smoking.value),
                time: parseFloat(form.time.value)
            };

            // Make prediction
            const prediction = await predictCVDRisk(patientData);

            // Display result
            displayPredictionResult(prediction);

            // Save to Firebase if user is logged in
            const user = firebase.auth().currentUser;
            if (user) {
                await savePredictionToFirebase(user.uid, prediction);
            }

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to get prediction. Please try again.');
        } finally {
            // Reset button
            submitButton.disabled = false;
            submitButton.textContent = 'Get Risk Assessment';
        }
    });
}

/**
 * Check if API is healthy
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const health = await response.json();

        if (health.status === 'healthy' && health.model_loaded) {
            console.log('API is ready');
            return true;
        } else {
            console.warn('API is not ready');
            return false;
        }
    } catch (error) {
        console.error('API is unreachable:', error);
        return false;
    }
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    // Check API health
    const apiReady = await checkAPIHealth();

    if (!apiReady) {
        console.error('Prediction API is not available');
        // Show warning to user
    }

    // Setup form handler
    setupFormHandler();
});

// Error handler
function handleError(error) {
    console.error('Error:', error);
    // Show user-friendly error message
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = 'Unable to complete assessment. Please try again.';
        errorElement.style.display = 'block';
    }
}

// Export functions if using modules
// export { predictCVDRisk, assessPatientFromFirebase, checkAPIHealth };
