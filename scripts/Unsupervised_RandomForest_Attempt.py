import os
import glob
import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.utils import resample
import matplotlib.pyplot as plt

data_path = "../data/training_data"
results_path = "../results"
data = []

print("Loading and preprocessing data...")
for sub_dir in sorted(os.listdir(data_path)):
    sub_dir_path = os.path.join(data_path, sub_dir)

    if os.path.isdir(sub_dir_path):
        humidity_file = glob.glob(os.path.join(sub_dir_path, "humidity_*.tif"))
        temperature_file = glob.glob(os.path.join(sub_dir_path, "temperature_*.tif"))

        if humidity_file and temperature_file:
            with rasterio.open(humidity_file[0]) as hum_src:
                humidity_data = hum_src.read(1).flatten()
            
            with rasterio.open(temperature_file[0]) as temp_src:
                temperature_data = temp_src.read(1).flatten()
            features = np.concatenate((humidity_data, temperature_data))
            data.append(features)
            
data = np.array(data)
print("Data shape:", data.shape)  # Inspect the dataset

# Generate Synthetic Data
print("Generating synthetic data...")
synthetic_data = resample(data, n_samples=len(data), random_state=42)

# Combine real and synthetic data
combined_data = np.vstack((data, synthetic_data))
labels = np.hstack((np.ones(len(data)), np.zeros(len(synthetic_data)))) 

# Train Random Forest Classifier
print("Training Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42, oob_score=False)
rf.fit(combined_data, labels)

# Extract leaf indices for proximity calculation
print("Extracting proximity matrix...")
leaf_indices = rf.apply(combined_data)

# Calculate proximity matrix
n_samples = len(combined_data)
proximity_matrix = np.zeros((n_samples, n_samples))

for i in range(n_samples):
    for j in range(n_samples):
        proximity_matrix[i, j] = np.mean(leaf_indices[i] == leaf_indices[j])

print("Proximity matrix calculated.")

# Perform Clustering
print("Performing clustering...")
linkage_matrix = linkage(proximity_matrix, method='ward')

dendrogram_file = os.path.join(results_path, "dendrogram.png")
plt.figure(figsize=(10, 7))
dendrogram(linkage_matrix)
plt.title("Hierarchical Clustering Dendrogram")
plt.xlabel("Sample Index")
plt.ylabel("Distance")
plt.savefig(dendrogram_file)
plt.show()
print(f"Dendrogram saved to {dendrogram_file}")

distance_threshold = 0.5
clusters = fcluster(linkage_matrix, t=distance_threshold, criterion='distance')

results_file = os.path.join(results_path, "RF_clustering_results.txt")
with open(results_file, "w") as f:
    for i, cluster in enumerate(clusters):
        f.write(f"Observation: {i}, Cluster: {cluster}\n")

print(f"Clustering results saved to {results_file}")