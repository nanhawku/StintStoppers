import { initializeApp } from 'firebase/app';
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, addDoc } from 'firebase/firestore';

// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyC4tOQCxX0XZLLAO6VKte4RVgd2RM4MnO8",
    authDomain: "comp-496.firebaseapp.com",
    projectId: "comp-496",
    storageBucket: "comp-496.firebasestorage.app",
    messagingSenderId: "412812122221",
    appId: "1:412812122221:web:7ff271b5628ccb98480764",
    measurementId: "G-37H72QTCEE"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// API Configuration
const API_BASE_URL = 'http://localhost:5000'; // Change to your deployed API URL

// ============================================
// AUTHENTICATION FUNCTIONS
// ============================================

/**
 * Sign up a new user
 */
export async function signUp(email, password) {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        console.log('User created:', userCredential.user.uid);
        return { success: true, user: userCredential.user };
    } catch (error) {
        console.error('Signup error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Sign in existing user
 */
export async function signIn(email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log('User signed in:', userCredential.user.uid);
        return { success: true, user: userCredential.user };
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Sign out current user
 */
export async function logOut() {
    try {
        await signOut(auth);
        console.log('User signed out');
        return { success: true };
    } catch (error) {
        console.error('Logout error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Monitor authentication state
 */
export function onAuthChange(callback) {
    return onAuthStateChanged(auth, callback);
}

/**
 * Get current user
 */
export function getCurrentUser() {
    return auth.currentUser;
}

// ============================================
// CVD PREDICTION FUNCTIONS
// ============================================

/**
 * Predict CVD risk for a single patient
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
 * Display prediction result to user
 */
function displayPredictionResult(prediction) {
    const resultDiv = document.getElementById('predictionResult');

    if (!prediction.success) {
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error:</strong> ${prediction.error || 'Unable to get prediction'}
            </div>
        `;
        resultDiv.style.display = 'block';
        return;
    }

    const riskClass = prediction.cvd_risk === 'YES' ? 'danger' : 'success';
    const riskIcon = prediction.cvd_risk === 'YES' ? '⚠️' : '✓';

    resultDiv.innerHTML = `
        <div class="alert alert-${riskClass} risk-result">
            <h3>${riskIcon} CVD Risk Assessment</h3>
            <div class="risk-details">
                <p><strong>Risk Status:</strong> <span class="risk-badge">${prediction.cvd_risk}</span></p>
                <p><strong>Risk Level:</strong> ${prediction.risk_level}</p>
                <p><strong>Probability:</strong> ${prediction.risk_percentage}</p>
            </div>
            ${prediction.cvd_risk === 'YES' ?
                '<p class="recommendation">⚕️ Please consult with a healthcare professional for proper evaluation.</p>' :
                '<p class="recommendation">Continue maintaining a healthy lifestyle.</p>'
            }
        </div>
    `;

    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Save prediction result to Firebase
 */
async function savePredictionToFirebase(patientData, prediction) {
    const user = getCurrentUser();

    if (!user) {
        throw new Error('User must be logged in to save data');
    }

    try {
        const docRef = await addDoc(collection(db, 'cvd_assessments'), {
            userId: user.uid,
            userEmail: user.email,
            patientName: patientData.patientName || 'Anonymous',
            patientData: {
                age: patientData.age,
                anaemia: patientData.anaemia,
                creatinine_phosphokinase: patientData.creatinine_phosphokinase,
                diabetes: patientData.diabetes,
                ejection_fraction: patientData.ejection_fraction,
                high_blood_pressure: patientData.high_blood_pressure,
                platelets: patientData.platelets,
                serum_creatinine: patientData.serum_creatinine,
                serum_sodium: patientData.serum_sodium,
                sex: patientData.sex,
                smoking: patientData.smoking,
                time: patientData.time
            },
            prediction: {
                cvd_risk: prediction.cvd_risk,
                risk_probability: prediction.risk_probability,
                risk_percentage: prediction.risk_percentage,
                risk_level: prediction.risk_level
            },
            timestamp: new Date()
        });

        console.log('Document written with ID:', docRef.id);
        return { success: true, documentId: docRef.id };

    } catch (error) {
        console.error('Error saving to Firebase:', error);
        throw error;
    }
}

/**
 * Check if API is healthy
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const health = await response.json();

        if (health.status === 'healthy' && health.model_loaded) {
            console.log('✓ API is ready');
            return true;
        } else {
            console.warn('⚠ API is not ready');
            return false;
        }
    } catch (error) {
        console.error('⚠ API is unreachable:', error);
        return false;
    }
}

// ============================================
// FORM HANDLER
// ============================================

/**
 * Handle CVD assessment form submission
 */
function setupCVDFormHandler() {
    const questionnaireForm = document.getElementById('questionnaireForm');

    if (!questionnaireForm) {
        console.error('Form with id="questionnaireForm" not found');
        return;
    }

    questionnaireForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Check if user is logged in
        const user = getCurrentUser();
        if (!user) {
            alert('You must be logged in to use this feature');
            return;
        }

        // Show loading state
        const submitButton = questionnaireForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Analyzing...';

        // Hide any previous results
        const resultDiv = document.getElementById('predictionResult');
        if (resultDiv) {
            resultDiv.style.display = 'none';
        }

        try {
            // Collect patient data from form
            const patientData = {
                patientName: document.getElementById('patientName')?.value || 'Anonymous',
                age: parseFloat(document.getElementById('age').value),
                anaemia: parseInt(document.getElementById('anaemia').value),
                creatinine_phosphokinase: parseFloat(document.getElementById('creatinine_phosphokinase').value),
                diabetes: parseInt(document.getElementById('diabetes').value),
                ejection_fraction: parseFloat(document.getElementById('ejection_fraction').value),
                high_blood_pressure: parseInt(document.getElementById('high_blood_pressure').value),
                platelets: parseFloat(document.getElementById('platelets').value),
                serum_creatinine: parseFloat(document.getElementById('serum_creatinine').value),
                serum_sodium: parseFloat(document.getElementById('serum_sodium').value),
                sex: parseInt(document.getElementById('sex').value),
                smoking: parseInt(document.getElementById('smoking').value),
                time: parseFloat(document.getElementById('time').value)
            };

            console.log('Sending data to ML model...');

            // Step 1: Get prediction from ML model (BLACK BOX)
            const prediction = await predictCVDRisk(patientData);
            console.log('Prediction received:', prediction);

            // Step 2: Display result to user
            displayPredictionResult(prediction);

            // Step 3: Save to Firebase (patient data + prediction result)
            console.log('Saving to Firebase...');
            await savePredictionToFirebase(patientData, prediction);

            // Success message
            setTimeout(() => {
                alert(`Assessment complete! Risk status: ${prediction.cvd_risk}\nData saved to database.`);
            }, 500);

        } catch (error) {
            console.error('Error during assessment:', error);

            // Show error to user
            const resultDiv = document.getElementById('predictionResult');
            if (resultDiv) {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Error:</strong> ${error.message}
                        <br><small>Please make sure the prediction API server is running.</small>
                    </div>
                `;
                resultDiv.style.display = 'block';
            } else {
                alert(`Error: ${error.message}`);
            }
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });
}

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize the application on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing CVD Assessment Application...');

    // Check API health
    const apiReady = await checkAPIHealth();
    if (!apiReady) {
        console.error('Prediction API is not available');
        const warningDiv = document.getElementById('apiWarning');
        if (warningDiv) {
            warningDiv.textContent = '⚠ Prediction API is offline. Please start the server: python3 api_server.py';
            warningDiv.style.display = 'block';
        }
    }

    // Setup form handler
    setupCVDFormHandler();

    // Monitor authentication state
    onAuthChange((user) => {
        const authSection = document.getElementById('authSection');
        const appSection = document.getElementById('appSection');
        const userEmailDisplay = document.getElementById('userEmail');

        if (user) {
            // User is logged in
            console.log('User logged in:', user.email);
            if (authSection) authSection.style.display = 'none';
            if (appSection) appSection.style.display = 'block';
            if (userEmailDisplay) userEmailDisplay.textContent = user.email;
        } else {
            // User is logged out
            console.log('User logged out');
            if (authSection) authSection.style.display = 'block';
            if (appSection) appSection.style.display = 'none';
        }
    });
});

// ============================================
// EXPORT FUNCTIONS FOR USE IN HTML
// ============================================

// Make authentication functions available globally
window.signUp = signUp;
window.signIn = signIn;
window.logOut = logOut;
window.getCurrentUser = getCurrentUser;
