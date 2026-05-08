#IMPORTS

# for the SQL commands
import sqlite3

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

# matplotlib and seaborn for data visualization
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.impute import SimpleImputer # missing value handler
from sklearn.preprocessing import LabelEncoder # to convert text labels to numbers
from sklearn.model_selection import train_test_split, GridSearchCV # splitting the dataset and hyperparameter tuning
from sklearn.metrics import accuracy_score # evaluation metric

# machine learning models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

# Set default font size
plt.rcParams['font.size'] = 24
from IPython.core.pylabtools import figsize

# LIME for explaining predictions
import lime 
import lime.lime_tabular

# for saving the model to files
import joblib

# 1. DATA CLEANING AND FORMATTING

sqldb = sqlite3.connect("choredistro_ml_dataset.db") # connect to SQLite database
data = pd.read_sql("SELECT * FROM chore_assignments", sqldb) # read table into pandas dataframe

print("Dataset preview:")
print(data.head()) # displays top of the dataframe

print("\nDataset info:")
print(data.info()) # see the column data types and non-missing values

print("\nStatistics of each column:")
print(data.describe()) # statistics for each column

def missing_values_table(df): # function to calculate missing values by column
    mis_val = df.isnull().sum() # total missing values
    mis_val_percent=100*df.isnull().sum()/len(df) # percentage of missing values
    mis_val_table=pd.concat([mis_val,mis_val_percent],axis=1) # make a table with the results
    mis_val_table_ren_columns=mis_val_table.rename(
        columns = {0 : 'Missing Values', 1 : '% of Total Values'}) # rename the columns
    mis_val_table_ren_columns=mis_val_table_ren_columns[
        mis_val_table_ren_columns.iloc[:,1]!=0].sort_values(
        '% of Total Values', ascending=False).round(1) # sort the table by percentage of missing descending
    print ("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"      
            "There are " + str(mis_val_table_ren_columns.shape[0]) +
            " columns that have missing values.") # print some summary information
    return mis_val_table_ren_columns # return the dataframe with missing information
    
print("\n")
print(missing_values_table(data)) # print the dataframe with missing information

data = data.drop(columns=["id", "chore_name"]) # drop unnecessary columns
                                                # id is just an identifier
                                                # chore_name is text and is not useful for the prediction

imputer = SimpleImputer(strategy="mean") # handle NULL values using mean replacement
numeric_cols = ["chore_difficulty","zain_pts","justin_pts","jasmine_pts","chloe_pts"] # columns with numeric values
data[numeric_cols] = imputer.fit_transform(data[numeric_cols]) # fills missing numeric values with the column mean

encoder = LabelEncoder()
data["assigned_to"] = LabelEncoder().fit_transform(data["assigned_to"])
data["assigned_to"] = data["assigned_to"].round(1)

data.to_csv('choredistro_ml_data_cleaned.csv', index=False) # convert the cleaned dataset to a CSV

# 2. EXPLORATORY DATA ANALYSIS

sns.countplot(x="assigned_to", data=data)
plt.title("Distribution of Chore Assignments")
plt.xlabel("Family Member")
plt.ylabel("Number of Chores")
plt.show()

corr = data.drop("assigned_to", axis=1).corr()
sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Feature Correlation Heatmap")
plt.show()

sns.pairplot(data, hue="assigned_to")
plt.show()

sns.kdeplot(data["chore_difficulty"], fill=True)
plt.title("Density Distribution of Chore Difficulty")
plt.show()

# 3. FEATURE ENGINEERING AND SELECTION

copy_of_data = data.copy() # copy the cleaned dataset

# separating the features and targets
features = copy_of_data.drop("assigned_to", axis=1)
targets = copy_of_data["assigned_to"]
targets_encoded = encoder.fit_transform(targets)

# split into 70% training and 30% testing set
X_train, X_test, Y_train, Y_test = train_test_split(features, targets_encoded, test_size = 0.3, random_state = 42)

# print the number of rows and columns in the training and testing set
print(X_train.shape)
print(X_test.shape)
print(Y_train.shape)
print(Y_test.shape)

# 4. BASELINE MODELS COMPARISON

# save the training and testing data
X_train.to_csv('training_features.csv', index = False)
X_test.to_csv('testing_features.csv', index = False)
# Convert the NumPy arrays to Pandas DataFrames before calling to_csv
pd.DataFrame(Y_train, columns=['assigned_member']).to_csv('training_labels.csv', index = False)      
pd.DataFrame(Y_test, columns=['assigned_member']).to_csv('testing_labels.csv', index = False)

# read in data into dataframes
train_features = pd.read_csv('training_features.csv')
test_features = pd.read_csv('testing_features.csv')
train_labels = pd.read_csv('training_labels.csv')
test_labels = pd.read_csv('testing_labels.csv')

# Display sizes of data
print('Training Feature Size: ', train_features.shape)
print('Testing Feature Size:  ', test_features.shape)
print('Training Labels Size:  ', train_labels.shape)
print('Testing Labels Size:   ', test_labels.shape)

# takes in a model, trains the model, and evaluates the model on the test set
def fit_and_evaluate(model):
    model.fit(X_train, Y_train) # Train the model

    # make predictions and evaluate
    predictions = model.predict(X_test)
    acc = accuracy_score(Y_test, predictions)

    return acc

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000),
    "Decision Tree": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(),
    "KNN": KNeighborsClassifier()
}

results = {}

for name, model in models.items():
    results[name] = fit_and_evaluate(model)
    print(f"\n{name} Accuracy:", results[name])

print("\nBest baseline model:", max(results, key=results.get)) # choose the best model

# plotting the accuracies on a bar graph
plt.figure(figsize=(8,5))

plt.barh(
    list(results.keys()),
    list(results.values())
)

plt.xlabel("Accuracy")
plt.title("Baseline Model Comparison")

plt.xlim(0,1)

plt.show()

# 5. HYPERPARAMETER TUNING

# Base model
log_reg_model = LogisticRegression(max_iter=5000)

# Hyperparameter search space
hyperparameter_grid = {
    "C": [0.001, 0.01, 0.1, 1, 10, 100],
    "solver": ["lbfgs", "saga", "newton-cg"]
}

# Random Search with Cross Validation
grid_search = GridSearchCV(
    estimator=log_reg_model,
    param_grid=hyperparameter_grid,
    cv=5,                  # 5-fold cross validation
    scoring="accuracy",
    n_jobs=-1
)

# Train search
grid_search.fit(X_train, Y_train)

# Best parameters found
print("Best Parameters:", grid_search.best_params_)

# 6. EVALUATE BEST MODEL

# Best tuned model
best_log_reg = grid_search.best_estimator_

# Predictions
Y_pred = best_log_reg.predict(X_test)
accuracy = accuracy_score(Y_test, Y_pred)

print("\nFinal Model Accuracy:", accuracy)

# 7. INTERPRET MODEL RESULTS

coefs = best_log_reg.coef_

# Extract the feature importances into a dataframe
feature_results = pd.DataFrame({'feature': list(train_features.columns), 
                                'importance': np.mean(np.abs(coefs), axis=0)})
# Show the top 10 most important
feature_results = feature_results.sort_values('importance', ascending=False).reset_index(drop=True)

print(f"Feature Importance:\n {feature_results}\n")

# plot feature importance
figsize(12, 10)
plt.style.use('fivethirtyeight')

# Plot the 10 most important features in a horizontal bar chart
feature_results.plot(x = 'feature', y = 'importance', edgecolor = 'k',
                     kind='barh', color = 'darkblue');
plt.xlabel('Relative Importance', size = 20); 
plt.ylabel('')
plt.title('Feature Importances from Logistic Regression', size = 30);
plt.show()

# LIME for explaining predictions
lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    training_data = train_features.values,
    feature_names = train_features.columns,
    class_names = best_log_reg.classes_,
    mode = "classification")

def predict_fn(x):
    return best_log_reg.predict_proba(pd.DataFrame(x, columns=X_train.columns))

# Pick the first test instance
instance = X_test.iloc[0].values

exp = lime_explainer.explain_instance(
    data_row = instance,
    predict_fn = predict_fn)  # predict_proba for classification

exp.as_pyplot_figure()

# 8. CONCLUSION / PREDICTION EXAMPLE
sample = [[70, 90, 10, 20, 10]]

feature_names = ['chore_difficulty', 'zain_pts', 'jasmine_pts', 'justin_pts', 'chloe_pts']
sample_df = pd.DataFrame(sample, columns=feature_names)

prediction = best_log_reg.predict(sample_df)
predicted_member = encoder.inverse_transform(prediction)

print("\nPredicted chore assignment:", predicted_member[0])

# Save the trained model and the encoder to files
joblib.dump(best_log_reg, 'choredistro_model.pkl')
joblib.dump(encoder, 'chore_encoder.pkl')
print("Model and encoder saved successfully!")