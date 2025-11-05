# Cardiovascular Disease Prediction with Explainable AI

This project aims to predict cardiovascular disease (CVD) using machine learning models and integrate explainable AI techniques such as SHAP and LIME to interpret the model's predictions. The dataset contains clinical data on patients, which is used to train multiple machine learning models. This repository provides the complete code for data preprocessing, model development, explainability, and evaluation of results.

## Project Objective
The main goal of this project is to build a predictive model for cardiovascular disease and explain the model's predictions using SHAP and LIME. The machine learning models aim to identify key clinical indicators that are critical to predicting CVD and provide insights into feature importance to enhance model transparency.

## Dataset
The dataset contains 299 records and 13 features that represent the clinical history of patients. Features include:
- Age
- Ejection Fraction
- Serum Creatinine
- Serum Sodium
- Time (follow-up period)
- Death Event (target variable)

## Project Workflow

1. **Exploratory Data Analysis (EDA):**
   - Visualizing distributions, relationships between features, and identifying outliers.
   - Generating correlation heatmaps and pair plots to uncover relationships between clinical features and CVD outcomes.

2. **Data Preprocessing:**
   - Handling missing values, removing duplicates, and normalizing continuous features.
   - Addressing class imbalance in the target variable using SMOTE (Synthetic Minority Over-sampling Technique).
   - Splitting the data into training (70%), validation (15%), and test (15%) sets.

3. **Model Development:**
   - Logistic Regression
   - Support Vector Machines (SVM) - Linear and RBF kernels
   - Random Forest Classifier
   - Fully Connected Neural Network (FCNN)
   - Convolutional Neural Network (CNN)

4. **Model Evaluation:**
   - Each model is evaluated using accuracy, precision, recall, F1-score, and confusion matrices.
     
5. **Explainable AI Integration:**
   - SHAP and LIME are applied to provide explanations for model predictions.
   - SHAP provides global explanations showing feature importance for each model.
   - LIME generates local explanations for specific predictions, offering insights into how individual features contribute to the outcome.

## Models Developed

- **Logistic Regression:** Achieved solid performance with an accuracy of 0.89.
- **SVM (Linear and RBF):** Competitive models with F1-scores around 0.82-0.85.
- **Random Forest:** Outperformed other models with an F1-score of 0.95.
- **FCNN (Fully Connected Neural Network):** Achieved the highest accuracy of 0.98 after hyperparameter tuning.
- **CNN (Convolutional Neural Network):** Designed to capture local patterns in features, achieving high recall of 0.96.

## Explainable AI Integration

- **SHAP (SHapley Additive exPlanations):**
  - SHAP was applied to all models to visualize global feature importance.
  - Key features like **Time**, **Ejection Fraction**, and **Serum Creatinine** were consistently highlighted across all models.
  
- **LIME (Local Interpretable Model-agnostic Explanations):**
  - LIME was used to provide local explanations for individual model predictions.
  - LIME helped confirm the contribution of features like **Age**, **Serum Sodium**, and **Ejection Fraction** to specific predictions.

## Requirements

To run this project, you will need the following Python libraries:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn lime shap tensorflow
