"""
Creates an example Excel template for patient data input
"""

import pandas as pd

# Create example patient data template
template_data = {
    'age': [65, 50, 45, 70, 55],
    'anaemia': [0, 1, 0, 1, 0],
    'creatinine_phosphokinase': [582, 7861, 120, 460, 1380],
    'diabetes': [0, 0, 0, 1, 0],
    'ejection_fraction': [20, 38, 60, 20, 35],
    'high_blood_pressure': [0, 0, 0, 1, 1],
    'platelets': [265000, 263358, 280000, 270000, 297000],
    'serum_creatinine': [1.9, 1.1, 1.0, 1.8, 1.2],
    'serum_sodium': [130, 136, 140, 134, 137],
    'sex': [1, 1, 0, 1, 0],
    'smoking': [0, 0, 1, 1, 0],
    'time': [4, 6, 150, 10, 90]
}

# Create DataFrame
df = pd.DataFrame(template_data)

# Add patient ID column
df.insert(0, 'patient_id', ['P001', 'P002', 'P003', 'P004', 'P005'])

# Save to Excel
output_file = 'patient_data_template.xlsx'
df.to_excel(output_file, index=False)

print(f"Template created: {output_file}")
print("\nColumn descriptions:")
print("  - patient_id: Unique patient identifier (optional)")
print("  - age: Age in years")
print("  - anaemia: 0 = No, 1 = Yes")
print("  - creatinine_phosphokinase: CPK enzyme level (mcg/L)")
print("  - diabetes: 0 = No, 1 = Yes")
print("  - ejection_fraction: Percentage of blood leaving the heart each contraction (%)")
print("  - high_blood_pressure: 0 = No, 1 = Yes")
print("  - platelets: Platelet count (kiloplatelets/mL)")
print("  - serum_creatinine: Serum creatinine level (mg/dL)")
print("  - serum_sodium: Serum sodium level (mEq/L)")
print("  - sex: 0 = Female, 1 = Male")
print("  - smoking: 0 = No, 1 = Yes")
print("  - time: Follow-up period (days)")
