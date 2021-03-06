# -----------------------> Importing the required Libraries -------------------------------

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------> Getting the dataset --------------------------------------------

data = pd.read_csv('Wholesale customers data.csv')

# -----------------------> Droppping the unwanted columns ---------------------------------

data.drop(['Region', 'Channel'], axis = 1, inplace = True)

# -----------------------> Selecting samples to explore data ------------------------------

indices = [47, 138, 359]
samples = data.iloc[indices]

# -----------------------> Checking for Null Values ---------------------------------------

data.isnull().any() # No Null values in the dataset. properly cleaned dataset

# -----------------------. Transforming the variables logarithmically ---------------------

ldata = np.log(data)

# -----------------------> Checking the dependency of variables -----------------------------

from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split

scores = []
for i in ldata.columns:

    feature = ldata.drop(i, axis = 1)
    target = ldata[i]

    X_train, X_test, y_train, y_test = train_test_split(feature, target, test_size = 0.2, random_state = 0)
    
    regressor = DecisionTreeRegressor(random_state = 0)
    regressor.fit(X_train, y_train)
    scores.append(regressor.score(X_test, y_test))
    
# -----------------------> Analyzing the trend Graphically ---------------------------------
    
sns.pairplot(data)
sns.pairplot(ldata)
    
# -----------------------> Detecting Outlier -----------------------------------------------

outliers = []

for i in ldata.columns:
    
    Q1 = np.percentile(ldata[i], 25)
    Q3 = np.percentile(ldata[i], 75)
    
    step = (Q3 - Q1) * 1.5
    
    outliers.append(ldata[(ldata[i] <= Q1 - step) | (ldata[i] >= Q3 + step )])
    
    ldata.drop(list(ldata[(ldata[i] <= Q1 - step) | (ldata[i] >= Q3 + step )].index), inplace = True)    
    ldata.reset_index(drop = True, inplace = True)

# -------------------------> Implementing the PCA Algorithm -------------------------------


from sklearn.decomposition import PCA

pca = PCA(n_components = 6, random_state = 0)
ldata_reduced = pca.fit_transform(ldata)

variance = pca.explained_variance_ratio_

dimension = ['Dimension1', 'Dimension2', 'Dimension3', 'Dimension4', 'Dimension5', 'Dimension6']
plt.figure(figsize = (10,6))
sns.barplot(variance, hue = ldata.columns)
plt.show()

pca = PCA(n_components = 2, random_state = 0)
ldata_reduced = pca.fit_transform(ldata)

plt.figure(figsize = (10, 6))
plt.scatter(x = ldata_reduced[:, 0], y = ldata_reduced[:, 1])
plt.show()

plt.figure(figsize = (10, 6))
sns.heatmap(ldata.corr())
plt.show()

corr_matrix = ldata.corr()

# -----------------------------> Trying KMeans Clustering ---------------------------------

wsrr = []
from sklearn.cluster import KMeans
for i in range(1, 6):
    kmean = KMeans(n_clusters = i, random_state = 0)
    kmean.fit(ldata_reduced)
    wsrr.append(kmean.inertia_)
    
plt.figure(figsize = (10,6))
sns.pointplot(y = wsrr, x = [i for i in range(1,6)])
plt.tight_layout
plt.show()

kmean = KMeans(n_clusters = 2, random_state = 0)
y_pred = kmean.fit_predict(ldata_reduced)

plt.figure(figsize = (10,6))
plt.scatter(x = ldata_reduced[y_pred == 0, 0], y = ldata_reduced[y_pred == 0, 1], color = 'red')
plt.scatter(x = ldata_reduced[y_pred == 1, 0], y = ldata_reduced[y_pred == 1, 1], color = 'blue')
plt.show()

# -----------------------------> Trying Gaussian Mixture ----------------------------------

from sklearn.mixture import GaussianMixture
gmm = GaussianMixture(n_components = 2, random_state = 0)
gmm.fit(ldata_reduced)

y_pred1 = gmm.predict(ldata_reduced)

plt.figure(figsize = (10,6))
plt.scatter(x = ldata_reduced[y_pred1 == 0, 0], y = ldata_reduced[y_pred1 == 0, 1], color = 'red')
plt.scatter(x = ldata_reduced[y_pred1 == 1, 0], y = ldata_reduced[y_pred1 == 1, 1], color = 'blue')
plt.show()

from sklearn.metrics import silhouette_score
score = silhouette_score(ldata_reduced, y_pred, random_state = 0)

# -----------------------------> Getting the centroid Data back ---------------------------

centres = gmm.means_

log_centre = pca.inverse_transform(centres)
true_centre = np.exp(log_centre)
centre = pd.DataFrame(data = true_centre, columns = data.columns)

