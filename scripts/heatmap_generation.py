import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import joblib

# use pre-trained model
model_filename = "random_forest_model.pkl"
model_path = f"../saved_model/{model_filename}"
rf = joblib.load(model_path)
print("Model loaded...")

# load test data
test_data_dir = "../data/saved_training_data"
x_test_filename = "X_test.npy"
y_test_filename = "y_test.npy"
X_test = np.load(os.path.join(test_data_dir, f"{x_test_filename}"))
y_test = np.load(os.path.join(test_data_dir, f"{y_test_filename}"))
print("Test data loaded...")

test_coordinates = [(x,y) for x,y in zip(range(len(X_test)), range(len(X_test)))]

y_prob = rf.predict_proba(X_test)[:, 1]

grid_size = 100
heatmap = np.zeros((grid_size, grid_size))

for (x,y), prediction in zip(test_coordinates, y_prob):
    grid_x = int(x % grid_size)
    grid_y = int(y % grid_size)
    heatmap[grid_x, grid_y] = prediction

plt.figure(figsize=(10, 8))
plt.title("Predicted Fires")
plt.imshow(heatmap, cmap="hot", interpolation="nearest")
plt.colorbar(label="Prediction")
plt.xlabel("X Coord")
plt.ylabel("Y Coord")

results_dir = "../results"
heatmap_path = os.path.join(results_dir, "fire_prediction_heatmap.png")
plt.savefig(heatmap_path)
print(f"Heatmap saved to: {heatmap_path}")
plt.close()