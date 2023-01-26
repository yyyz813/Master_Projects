# -*- coding: utf-8 -*-
"""Assignment 4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pJUiOJdp0fCISoFUEgmAkOgKkr9dGfJk

---

<center><h1>Assignment 4</h1></center>

---

# 1. <font color='#556b2f'> **Support Vector Machines with Synthetic Data**</font>, 50 points.

For this problem, we will generate synthetic data for a nonlinear binary classification problem and partition it into training, validation and test sets. Our goal is to understand the behavior of SVMs with Radial-Basis Function (RBF) kernels with different values of $C$ and $\gamma$.
"""

# DO NOT EDIT THIS FUNCTION; IF YOU WANT TO PLAY AROUND WITH DATA GENERATION, 
# MAKE A COPY OF THIS FUNCTION AND THEN EDIT

import numpy as np
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def generate_data(n_samples, tst_frac=0.2, val_frac=0.2):
  # Generate a non-linear data set
  X, y = make_moons(n_samples=n_samples, noise=0.25, random_state=42)
   
  # Take a small subset of the data and make it VERY noisy; that is, generate outliers
  m = 30
  np.random.seed(30)  # Deliberately use a different seed
  ind = np.random.permutation(n_samples)[:m]
  X[ind, :] += np.random.multivariate_normal([0, 0], np.eye(2), (m, ))
  y[ind] = 1 - y[ind]

  # Plot this data
  cmap = ListedColormap(['#b30065', '#178000'])  
  plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap, edgecolors='k')       
  
  # First, we use train_test_split to partition (X, y) into training and test sets
  X_trn, X_tst, y_trn, y_tst = train_test_split(X, y, test_size=tst_frac, 
                                                random_state=42)

  # Next, we use train_test_split to further partition (X_trn, y_trn) into training and validation sets
  X_trn, X_val, y_trn, y_val = train_test_split(X_trn, y_trn, test_size=val_frac, 
                                                random_state=42)
  
  return (X_trn, y_trn), (X_val, y_val), (X_tst, y_tst)

#
#  DO NOT EDIT THIS FUNCTION; IF YOU WANT TO PLAY AROUND WITH VISUALIZATION, 
#  MAKE A COPY OF THIS FUNCTION AND THEN EDIT 
#

def visualize(models, param, X, y):
  # Initialize plotting
  if len(models) % 3 == 0:
    nrows = len(models) // 3
  else:
    nrows = len(models) // 3 + 1
    
  fig, axes = plt.subplots(nrows=nrows, ncols=3, figsize=(15, 5.0 * nrows))
  cmap = ListedColormap(['#b30065', '#178000'])

  # Create a mesh
  xMin, xMax = X[:, 0].min() - 1, X[:, 0].max() + 1
  yMin, yMax = X[:, 1].min() - 1, X[:, 1].max() + 1
  xMesh, yMesh = np.meshgrid(np.arange(xMin, xMax, 0.01), 
                             np.arange(yMin, yMax, 0.01))

  for i, (p, clf) in enumerate(models.items()):
    # if i > 0:
    #   break
    r, c = np.divmod(i, 3)
    ax = axes[r, c]

    # Plot contours
    zMesh = clf.decision_function(np.c_[xMesh.ravel(), yMesh.ravel()])
    zMesh = zMesh.reshape(xMesh.shape)
    ax.contourf(xMesh, yMesh, zMesh, cmap=plt.cm.PiYG, alpha=0.6)

    if (param == 'C' and p > 0.0) or (param == 'gamma'):
      ax.contour(xMesh, yMesh, zMesh, colors='k', levels=[-1, 0, 1], 
                 alpha=0.5, linestyles=['--', '-', '--'])

    # Plot data
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap, edgecolors='k')       
    ax.set_title('{0} = {1}'.format(param, p))

# Generate the data
n_samples = 300    # Total size of data set 
(X_trn, y_trn), (X_val, y_val), (X_tst, y_tst) = generate_data(n_samples)

"""---
### **a**. (25 points)  The effect of the regularization parameter, $C$
Complete the Python code snippet below that takes the generated synthetic 2-d data as input and learns non-linear SVMs. Use scikit-learn's [SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html) function to learn SVM models with **radial-basis kernels** for fixed $\gamma$ and various choices of $C \in \{10^{-3}, 10^{-2}\, \cdots, 1, \, \cdots\, 10^5\}$. The value of $\gamma$ is fixed to $\gamma = \frac{1}{d \cdot \sigma_X}$, where $d$ is the data dimension and $\sigma_X$ is the standard deviation of the data set $X$. SVC can automatically use these setting for $\gamma$ if you pass the argument gamma = 'scale' (see documentation for more details).

**Plot**: For each classifier, compute **both** the **training error** and the **validation error**. Plot them together, making sure to label the axes and each curve clearly.

**Discussion**: How do the training error and the validation error change with $C$? Based on the visualization of the models and their resulting classifiers, how does changing $C$ change the models? Explain in terms of minimizing the SVM's objective function $\frac{1}{2} \mathbf{w}^\prime \mathbf{w} \, + \, C \, \Sigma_{i=1}^n \, \ell(\mathbf{w} \mid \mathbf{x}_i, y_i)$, where $\ell$ is the hinge loss for each training example $(\mathbf{x}_i, y_i)$.

**Final Model Selection**: Use the validation set to select the best the classifier corresponding to the best value, $C_{best}$. Report the accuracy on the **test set** for this selected best SVM model. _Note: You should report a single number, your final test set accuracy on the model corresponding to $C_{best}$_.
"""

# Learn support vector classifiers with a radial-basis function kernel with
# fixed gamma = 1 / (n_features * X.std()) and different values of C 
from sklearn.svm import SVC

C_range = np.arange(-3.0, 6.0, 1.0)
C_values = np.power(10.0, C_range)

models = dict()
trnErr = dict()
valErr = dict()

# While C in range and different values
for value in C_values:

    clf = SVC(C=value,kernel='rbf',gamma='scale')  # Classifier, if gamma='scale' (default) is passed then it uses 1 / (n_features * X.var()) as value of gamma,
    clf.fit(X_trn, y_trn)
    models[value] = clf
    trnErr[value] = 1 - models[value].score(X_trn, y_trn)  # Return mean accuracy, error = 1 - score
    valErr[value] = 1 - models[value].score(X_val, y_val)
    
#visualization    
visualize(models, 'C', X_trn, y_trn)

plt.figure()
plt.title("The effect of the regularization parameter C in SVM",fontsize=12)


plt.plot(C_range, [trnErr[value] for value in C_values], marker='D', linestyle='dashed' , linewidth=2, markersize=9)
plt.plot(C_range, [valErr[value] for value in C_values], marker='o', linestyle='dashed' , linewidth=2, markersize=9)

plt.xlabel("Regularized Parameter C", fontsize=12)
plt.ylabel("Training Error vs. Validation Error", fontsize=12)

plt.xticks(C_range, [str(round(value)) for value in C_range], fontsize=12)
plt.axis([min(C_range) - 1, max(C_range) + 1, -0.1, 1])
plt.legend(["Training Error", "Validation Error"], fontsize=16)

# Find minimum error and plot
best_C = 0
min_error = 1

for (i, j) in valErr.items():
    if (j < min_error):
        min_error = j
        best_C = i
testAccuracy = models[best_C].score(X_tst, y_tst)

print("Best C value is: {0:} , Test Accuracy is: {1:.3f}.".format(best_C, testAccuracy))
plt.plot([np.log10(best_C)], [min_error], marker='*', color='black', linewidth=3, markersize=16)

"""---
### **b**. (25 points)  The effect of the RBF kernel parameter, $\gamma$
Complete the Python code snippet below that takes the generated synthetic 2-d data as input and learns various non-linear SVMs. Use scikit-learn's [SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html) function to learn SVM models with **radial-basis kernels** for fixed $C$ and various choices of $\gamma \in \{10^{-2}, 10^{-1}\, 1, 10, \, 10^2 \, 10^3\}$. The value of $C$ is fixed to $C = 10$.

**Plot**: For each classifier, compute **both** the **training error** and the **validation error**. Plot them together, making sure to label the axes and each curve clearly.

**Discussion**: How do the training error and the validation error change with $\gamma$? Based on the visualization of the models and their resulting classifiers, how does changing $\gamma$ change the models? Explain in terms of the functional form of the RBF kernel, $\kappa(\mathbf{x}, \,\mathbf{z}) \, = \, \exp(-\gamma \cdot \|\mathbf{x} - \mathbf{z} \|^2)$

**Final Model Selection**: Use the validation set to select the best the classifier corresponding to the best value, $\gamma_{best}$. Report the accuracy on the **test set** for this selected best SVM model. _Note: You should report a single number, your final test set accuracy on the model corresponding to $\gamma_{best}$_.
"""

# Learn support vector classifiers with a radial-basis function kernel with 
# fixed C = 10.0 and different values of gamma
gamma_range = np.arange(-2.0, 4.0, 1.0)
gamma_values = np.power(10.0, gamma_range)

models = dict()
trnErr = dict()
valErr = dict()

# While gamma in range and different values
for value in gamma_values:

    clf = SVC(C=10, kernel='rbf', gamma=value)  # fixed C = 10
    clf.fit(X_trn, y_trn)
    models[value] = clf
    trnErr[value] = 1 - models[value].score(X_trn, y_trn)  
    valErr[value] = 1 - models[value].score(X_val, y_val)

#visualization   
visualize(models, 'gamma', X_trn, y_trn)

plt.figure()
plt.title("The effect of the RBF kernel parameter gamma in SVM", fontsize=12)

plt.plot(gamma_range, [trnErr[value] for value in gamma_values], marker='D', linestyle='dashed', linewidth=2, markersize=9)
plt.plot(gamma_range, [valErr[value] for value in gamma_values], marker='o', linestyle='dashed',linewidth=2, markersize=9)

plt.xlabel("RBF kernel parameter gamma", fontsize=12)
plt.ylabel("Training Error vs. Validation Error", fontsize=12)

plt.xticks(gamma_range, [str(round(value)) for value in gamma_range], fontsize=12)
plt.axis([min(gamma_range) - 1, max(gamma_range) + 1, -0.1, 1])
plt.legend(["Training Error", "Validation Error"], fontsize=16)

# Find minimum error and plot
best_gamma = 0
min_error = 1

for (i, j) in valErr.items():
    if (j < min_error):
        min_error = j
        best_gamma = i
testAccuracy = models[best_gamma].score(X_tst, y_tst)

print("The best value of gamma is : {0:}, Test Accuracy is: {1:.3f}.".format(best_gamma, testAccuracy))
plt.plot([np.log10(best_gamma)], [min_error], marker='*', color='black', linewidth=3, markersize=16)

"""---
# 2. <font color='#556b2f'> **Breast Cancer Diagnosis with Support Vector Machines**</font>, 25 points.

For this problem, we will use the [Wisconsin Breast Cancer](https://archive.ics.uci.edu/ml/datasets/Breast+Cancer+Wisconsin+(Diagnostic)) data set, which has already been pre-processed and partitioned into training, validation and test sets. Numpy's [loadtxt](https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.loadtxt.html) command can be used to load CSV files.
"""

# Load the Breast Cancer Diagnosis data set; download the files from eLearning
# CSV files can be read easily using np.loadtxt()


training = np.loadtxt(open("wdbc_trn.csv", "rb"), delimiter=",")
X_trn = training[:,1:]
y_trn = training[:,0]

testing = np.loadtxt(open("wdbc_tst.csv", "rb"), delimiter=",")
X_tst = testing[:,1:]
y_tst = testing[:,0]

validating = np.loadtxt(open("wdbc_val.csv", "rb"), delimiter=",")
X_val = validating[:,1:]
y_val = validating[:,0]

"""Use scikit-learn's [SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html) function to learn SVM models with **radial-basis kernels** for **each combination** of $C \in \{10^{-2}, 10^{-1}, 1, 10^1, \, \cdots\, 10^4\}$ and $\gamma \in \{10^{-3}, 10^{-2}\, 10^{-1}, 1, \, 10, \, 10^2\}$. Print the tables corresponding to the training and validation errors.

**Final Model Selection**: Use the validation set to select the best the classifier corresponding to the best parameter values, $C_{best}$ and $\gamma_{best}$. Report the accuracy on the **test set** for this selected best SVM model. _Note: You should report a single number, your final test set accuracy on the model corresponding to $C_{best}$ and $\gamma_{best}$_.
"""

from sklearn.metrics import accuracy_score

C_range = np.arange(-2.0, 5.0, 1.0)
C_values = np.power(10.0, C_range)

gamma_range = np.arange(-3.0, 3.0, 1.0)
gamma_values = np.power(10.0, gamma_range)

list_C = list(C_values)
list_gamma = list(gamma_values)

best_c = []
best_gamma = []
test_Err = []

reduce_Err = 1

for i,c in  enumerate(C_values):    # Iteration through each C and gamma pairs
    for j,g in enumerate(gamma_values):
        
        clf = SVC(C=c,kernel='rbf',gamma=g)
        clf.fit(X_trn, y_trn)
        
        p_y_val = clf.predict(X_val)
        p_y_test = clf.predict(X_tst)
        
        err_valid = 1 - accuracy_score(y_val, p_y_val)
        err_test = 1 - accuracy_score(y_tst, p_y_test)
             
        if(err_valid < reduce_Err ):
            reduce_Err = err_valid
            
            best_c.clear()  # limit redundent through iteration
            best_gamma.clear()
            test_Err.clear()
            
            best_c.append(list_C[i])
            best_gamma.append(list_gamma[j])
            test_Err.append(err_test)
            
        elif (err_valid == reduce_Err ):
                best_c.append(list_C[i])
                best_gamma.append(list_gamma[j])
                test_Err.append(err_test)
                
final_accracy = 1 - reduce_Err
                
print("C values : ",best_c)
print("Gamma values : ",best_gamma)
print("Test error with corresponding C and gamma pairs : ", test_Err)
print("Error Reduce : ",reduce_Err * 100)
print("Final test set accuracy on the model corresponding to the best C and gamma: ", final_accracy * 100)

"""---
# 3. <font color='#556b2f'> **Breast Cancer Diagnosis with $k$-Nearest Neighbors**</font>, 25 points.

Use scikit-learn's [k-nearest neighbor](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html) classifier to learn models for Breast Cancer Diagnosis with $k \in \{1, \, 5, \, 11, \, 15, \, 21\}$, with the kd-tree algorithm.

**Plot**: For each classifier, compute **both** the **training error** and the **validation error**. Plot them together, making sure to label the axes and each curve clearly.

**Final Model Selection**: Use the validation set to select the best the classifier corresponding to the best parameter value, $k_{best}$. Report the accuracy on the **test set** for this selected best kNN model. _Note: You should report a single number, your final test set accuracy on the model corresponding to $k_{best}$_.
"""

from sklearn.neighbors import KNeighborsClassifier

K_values = [1, 5, 11, 15, 21]
best_k = 0
min_error = 1


models = dict()
trnErr = []
valErr = []

for value in K_values:

    clf = KNeighborsClassifier(n_neighbors= value)
    clf.fit(X_trn, y_trn)
    models[value] = clf

    trnErr.append(1 - models[value].score(X_trn, y_trn))  
    valErr.append(1 - models[value].score(X_val, y_val))

    if (valErr[-1] < min_error):
        min_error = valErr[-1]
        best_k = value


# Visualization
plt.figure()
plt.title("kd-tree algorithm for the Breast Cancer dataset ")

plt.plot(K_values, trnErr, marker='D', linestyle='dashed', linewidth=2, markersize=9)
plt.plot(K_values, valErr, marker='o', linestyle='dashed', linewidth=2, markersize=9)

plt.xlabel("k neatest neighbor value", fontsize=12)
plt.ylabel("Training Error vs. Validation Error", fontsize=12)

plt.axis([min(K_values) - 1, max(K_values) + 1, -0.1, 1])
plt.legend(["Training Error", "Validation Error"], fontsize=16)

testAccuracy = models[best_k].score(X_tst, y_tst)
print("Best k value is: {0:}, Test accuracy is: {1:.3f}.".format(best_k, testAccuracy))
plt.plot([best_k], [min_error], marker='*', color='black', linewidth=3, markersize=16)

"""**Discussion**: Which of these two approaches, SVMs or kNN, would you prefer for this classification task? Explain."""