import os
import glob
import numpy as np
import rasterio
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from pathlib import Path
import matplotlib.pyplot as plt

data_path = "../data/training_data"
results_path = "../results"

os.makedirs(results_path, exist_ok=True)

data = []

# Load and preprocess data
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

print("Applying PCA...")
pca = PCA(n_components=2)
data_pca = pca.fit_transform(data)

print("Applying K-Means clustering...")
kmeans = KMeans(n_clusters=3, random_state=0)
clusters = kmeans.fit_predict(data_pca)
results_file = os.path.join(results_path, "clustering_results.txt")
with open(results_file, "w") as f:
    for i, cluster in enumerate(clusters):
        f.write(f"Subdirectory: {i}, Cluster: {cluster}\n")

# Plot clusters (optional, if PCA was used)
plt.scatter(data_pca[:, 0], data_pca[:, 1], c=clusters, cmap='viridis')
plt.title("Clustering Results")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.colorbar(label="Cluster")
plt.savefig(os.path.join(results_path, "clustering_plot.png"))
plt.show()

print("Clustering results saved to:", results_file)