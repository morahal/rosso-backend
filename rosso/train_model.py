import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
#file_path = '/path/to/your/dataset.csv'  # Change this to your actual file path
data = pd.read_csv("./final_test.csv")

#data = data.drop_duplicates()

# Handle missing values
imputer = SimpleImputer(strategy='median')
data[['age', 'height']] = imputer.fit_transform(data[['age', 'height']])

# Encode 'size' column
size_encoder = OrdinalEncoder(categories=[['XXS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']])
data['size'] = size_encoder.fit_transform(data[['size']])

# Separate features and target variable
X = data.drop('size', axis=1)
y = data['size']

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Initialize and train models
# Random Forest with basic hyperparameter tuning
random_forest_tuned = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
random_forest_tuned.fit(X_train, y_train)

# Gradient Boosting
# gradient_boosting = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
# gradient_boosting.fit(X_train, y_train)

# Predict and evaluate
y_pred_rf_tuned = random_forest_tuned.predict(X_test)
# y_pred_gb = gradient_boosting.predict(X_test)

accuracy_rf_tuned = accuracy_score(y_test, y_pred_rf_tuned)
# accuracy_gb = accuracy_score(y_test, y_pred_gb)

print(f"Random Forest Tuned Accuracy: {accuracy_rf_tuned:.4f}")
# print(f"Gradient Boosting Accuracy: {accuracy_gb:.4f}")




# Save the models
joblib.dump(random_forest_tuned, './model_files/random_forest_tuned.joblib')

# Save these objects to joblib files
joblib.dump(imputer, './model_files/imputer.joblib')
joblib.dump(size_encoder, './model_files/size_encoder.joblib')
joblib.dump(scaler, './model_files/scaler.joblib')