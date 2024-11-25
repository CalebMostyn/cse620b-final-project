# This is the script responsible for creating, training and testing the model.
# Will rely on make_training_set.py in order to create a dataset of sample points
# from the corresponding datasets.

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Change based off of the labels given to each classifier
X = data[['NDVI', 'NDMI', 'BurnAreaIndex', 'LandSurfaceTemp', 'AirTemp', 'Humidity', 'BurnedArea_MODIS', 'VI_MODIS']]
y = data['Wildfire']

# Change based off of the % split between train/test data from the dataset
test_perc = 0.3

# Split data and train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_perc, random_state=0)
model = RandomForestClassifier(n_estimators=100, random_state=0)
model.fit(X_train, y_train)

# Example evaluations of model
y_pred = model.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred)
