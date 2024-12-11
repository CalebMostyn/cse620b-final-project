import os
import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.tree import plot_tree
import joblib
import matplotlib.pyplot as plt

# Data
data_dir = "../data/training_data" # path of training data
os.makedirs(data_dir, exist_ok=True)
data_points = 3540 # number of data points in data_dir
random_seed = 700 # random seed state

# Model 
save_dir = "../saved_model" # location to save model
os.makedirs(save_dir, exist_ok=True)
model_filename = "random_forest_model.pkl" # name of saved model file

# Results
results_dir = "../results"
os.makedirs(results_dir, exist_ok=True)

def load_data(root_path):
    # Debugging
    # for i in range(10):
    #     data_path = os.path.join(root_path, f"data_point_{str(i)}")
    #     print(data_path)

    features, labels = [], []
    for i in range(data_points):
        if i % 100 == 0 and i != 0:
            print(f"Processed {i} directories...", flush=True)
        data_path = os.path.join(root_path, f"data_point_{str(i)}")
        if not os.path.isdir(data_path):
            print("Error loading file: " + data_path)
            continue

        feature_row = []
        label = None

        for file in os.listdir(data_path):
            file_path = os.path.join(data_path, file)
            if file.endswith(".tif"):
                with rasterio.open(file_path) as src:
                    array = src.read(1)
                    if "fire_occured" in file: 
                        label = int(array.mean() > 0)
                    else: 
                        feature_row.append(array.mean())

        if label is not None:
            features.append(feature_row)
            labels.append(label)

    print("Finished loading data...", flush=True)
    return np.array(features, dtype=np.float32), np.array(labels, dtype=np.int32)

# Load data
print("Loading data...", flush=True)
features, labels = load_data(data_dir)

# Train model
print("Starting model training...", flush=True)
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=random_seed)
rf = RandomForestClassifier(n_estimators=100, random_state=random_seed)
rf.fit(X_train, y_train)

# Test model
print("Starting model testing...", flush=True)
y_pred = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}", flush=True)

# Features
print("Generating feature importance...")
feature_importance = rf.feature_importances_
feature_names = ["Air Temp", "BAI", "Humidity", "Land Temp", "NDMI", "NDVI"]

plt.figure(figsize=(10,6))
plt.barh(feature_names, feature_importance, color="skyblue")
plt.xlabel("Importance")
plt.title("Feature Importance in Random Forest")
plt.tight_layout()
plt.savefig(os.path.join(results_dir, "feature_importance.png"))
plt.close()

# Confusion Matrix
print("Generating confusion matrix...")
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Fire", "Fire"])
disp.plot(cmap="Blues", values_format="d")
plt.title("Confusion Matrix")
plt.savefig(os.path.join(results_dir, "confusion_matrix.png"))
plt.close()

# Plot Tree
print("Generating tree plot...")
plt.figure(figsize=(12,8))
plot_tree(rf.estimators_[0], feature_names=feature_names, class_names=["No Fire", "Fire"], filled=True, max_depth=3)
plt.title("Sample Decision Tree (max_depth=3)")
plt.savefig(os.path.join(results_dir, "sample_tree(depth=3).png"))
plt.close


# Save Model
model_path = os.path.join(save_dir, model_filename)
joblib.dump(rf, model_path)
print(f"Model saved to {model_path}", flush=True)


