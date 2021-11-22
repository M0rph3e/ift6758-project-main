# %% [markdown]
# ## Base Model Q3

# %%

# %%
# Import comet_ml at the top of your file, before sklearn!
from comet_ml import Experiment
import os 

# Create an experiment with your api key
comet_exp = Experiment(
    api_key=os.environ.get('COMET_API_KEY'),  # don’t hardcode!!
    project_name="milestone_2",
    workspace="morph-e",
)


# %%
from ift6758.features.feature_engineering1 import SeasonDataSet
from ift6758.metrics import plot_metrics
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
import numpy as np
import os
import random
import joblib


# %%
def seed_everything(seed_value):
    random.seed(seed_value)
    np.random.seed(seed_value)
    os.environ['PYTHONHASHSEED'] = str(seed_value)
    
seed = 42
seed_everything(seed)

# %%
train_years = [2015,2016,2017]
val_years = [2018]
test_years=[2019]


# %%
train_dataset = SeasonDataSet(train_years)
train_df = train_dataset.get_tidy_data()
train_df.head()

# %%
val_dataset = SeasonDataSet(val_years)
val_df = val_dataset.get_tidy_data()
val_df.head()

# %%
# train_df["angleNet"]=np.abs(train_df["angleNet"])
# val_df["angleNet"]=np.abs(val_df["angleNet"])


# %%
train_df.isnull().sum() ##No nulls in our features

# %%
train_df["result.emptyNet"].value_counts()

# %%
train_df["result.event"].value_counts()

# %%
from sklearn import preprocessing


# %%
def XY(df,label_column,features):
    X = df.drop([label_column],axis=1)[features]
    Y = df[label_column]
    # scaler = preprocessing.MinMaxScaler()
    # X=scaler.fit_transform(X)

    return X,Y

# %%
predscore_val_dict={}


# %%
weights_dir = "../ift6758/models/weights/"

# %% [markdown]
# ## logreg-dis

# %%
experiment = "logreg-dis"
features = ["distanceNet"]
label_column = "isGoal"

## Splitting X and Y
Xtrain,Ytrain = XY(train_df,label_column,features)
Xval,Yval = XY(val_df,label_column,features)

## Training
clf = LogisticRegression()
clf.fit(Xtrain, Ytrain)
y_pred_val  = clf.predict(Xval)
y_pred_val_scores = clf.predict_proba(Xval)[:,1]

plot_metrics.plotConfusion(Yval,y_pred_val,title=experiment)

predscore_val_dict[experiment]={}
predscore_val_dict[experiment]['val']=Yval
predscore_val_dict[experiment]['predscore']=y_pred_val_scores

## Dumping model
filename=f"{weights_dir}/{experiment}-yearvalidation.pkl"
joblib.dump(clf,filename)

# %% [markdown]
# ## logreg-angle

# %%
experiment = "logreg-angle"
features = ["angleNet"]
label_column = "isGoal"

## Splitting X and Y
Xtrain,Ytrain = XY(train_df,label_column,features)
Xval,Yval = XY(val_df,label_column,features)

## Training
clf = LogisticRegression()
clf.fit(Xtrain, Ytrain)
y_pred_val  = clf.predict(Xval)
y_pred_val_scores = clf.predict_proba(Xval)[:,1]

plot_metrics.plotConfusion(Yval,y_pred_val,title=experiment)

predscore_val_dict[experiment]={}
predscore_val_dict[experiment]['val']=Yval
predscore_val_dict[experiment]['predscore']=y_pred_val_scores



## Dumping model
filename=f"{weights_dir}/{experiment}-yearvalidation.pkl"
joblib.dump(clf,filename)

# %% [markdown]
# ## logreg-dis-angle

# %%
experiment = "logreg-dis-angle"
features = ["distanceNet","angleNet"]
label_column = "isGoal"

## Splitting X and Y
Xtrain,Ytrain = XY(train_df,label_column,features)
Xval,Yval = XY(val_df,label_column,features)

## Training
clf = LogisticRegression()
clf.fit(Xtrain, Ytrain)
y_pred_val  = clf.predict(Xval)
y_pred_val_scores = clf.predict_proba(Xval)[:,1]

plot_metrics.plotConfusion(Yval,y_pred_val,title=experiment)

predscore_val_dict[experiment]={}
predscore_val_dict[experiment]['val']=Yval
predscore_val_dict[experiment]['predscore']=y_pred_val_scores



## Dumping model
filename=f"{weights_dir}/{experiment}-yearvalidation.pkl"
joblib.dump(clf,filename)

# %% [markdown]
# * It's always pedicting 0, although about 10% of data is 1
# * (Need to explore) Why it's happening (Mostly because the features - diatance,angle values are similar for 1 and 0), and output of predict is 0 or 1 with probability threshold 0.5

# %% [markdown]
# ## Dummy Classifier

# %%
experiment = "uniform-sampling"
features = ["distanceNet","angleNet"]
label_column = "isGoal"

## Splitting X and Y
Xtrain,Ytrain = XY(train_df,label_column,features)
Xval,Yval = XY(val_df,label_column,features)



y_pred_val_scores = np.random.uniform(0,1,Xval.shape[0])
y_pred_val = (y_pred_val_scores>=0.5)
plot_metrics.plotConfusion(Yval,y_pred_val,title=experiment)

predscore_val_dict[experiment]={}
predscore_val_dict[experiment]['val']=Yval
predscore_val_dict[experiment]['predscore']=y_pred_val_scores



## Dumping model
filename=f"{weights_dir}/{experiment}-yearvalidation.pkl"
joblib.dump(clf,filename)

# %%
# Yscores[2].shape[0]/(Ytrain.shape[0]+Yscores[2].shape[0])

# %%
experiments = predscore_val_dict.keys()
Ytrues=[predscore_val_dict[experiment]['val'] for experiment in experiments]
Yscores=[predscore_val_dict[experiment]['predscore'] for experiment in experiments]
plot_labels=experiments


# %% [markdown]
# ## ROC_AUC
# 

# %%
plot_metrics.plot_roc(Ytrues,Yscores,plot_labels)

# %% [markdown]
# ## Model Percentile

# %%
plot_metrics.plot_percentile(Ytrues,Yscores,bin_width=5,plot_labels=plot_labels)

# %% [markdown]
# ## Calibrarion Curve

# %%
plot_metrics.plot_calibration(Ytrues,Yscores,plot_labels=plot_labels)

# %%
experiments

# %%
comet_exp.log_model("logreg distance validation on 2018", f"{weights_dir}/logreg-dis-yearvalidation.pkl")
comet_exp.log_model("logreg angle validation on 2018", f"{weights_dir}/logreg-angle-yearvalidation.pkl")
comet_exp.log_model("logreg distance angle validation on 2018", f"{weights_dir}/logreg-dis-angle-yearvalidation.pkl")
comet_exp.log_model("logreg uniform sampling validation on 2018", f"{weights_dir}/uniform-sampling-yearvalidation.pkl")
comet_exp.end()

# %%



