import pandas as pd
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn import metrics, preprocessing

def standardize_features():
    
    data_dir = os.getcwd().replace('/src', '') + '/data/interim'
    interim_modeling_df = pd.read_csv("{}/step3_interim_modeling_data.csv".format(data_dir))
    
    #sorry...this is messy. just checks to see if there are columns w/data type of float and 1,0
    # then casts as bool
    for col in interim_modeling_df.columns.values:
        if interim_modeling_df[pred_col].dtype == "float64":
            if len(interim_modeling_df[pred_col].unique()) == 2 \
                and 1 in interim_modeling_df[pred_col].unique() \
                and 0 in interim_modeling_df[pred_col].unique():
            
            interim_modeling_df[pred_col] = interim_modeling_df[pred_col].astype(bool)
    
    interim_pred_df, interim_response_df = fill_na(interim_modeling_df)
    
    model_1_pred_train, model_2_pred_train, model_1_response_train, model_2_response_train = \
        train_test_split(interim_pred_df, interim_response_df, test_size=0.5, random_state=223)
    
    for pred_col in pred_train.columns.values:
        if pred_train[pred_col].dtype == "float64":
            print("standardizing {}".format(pred_col))
            scaler = preprocessing.StandardScaler().fit(pred_train[[pred_col]])
            train_col_scaled = scaler.transform(pred_train[[pred_col]])
            test_col_scaled = scaler.transform(pred_test[[pred_col]])
            pred_train["{}_stdized".format(pred_col)] = train_col_scaled
            pred_test["{}_stdized".format(pred_col)] = test_col_scaled
            #pred_train = pred_train.drop(pred_col, axis=1)
            #pred_test = pred_test.drop(pred_col, axis=1)
            
def fill_na(interim_modeling_df):

    nobs = float(len(interim_modeling_df))
    
    for col in interim_modeling_df.columns.values:

        num_nulls = float(interim_modeling_df[col].isnull().sum())

        if num_nulls / nobs > .1 or len(interim_modeling_df[col].unique()) == 1:

            interim_modeling_df = interim_modeling_df.drop(col, axis = 1)

        elif num_nulls > 0:
            if interim_modeling_df[col].dtype == "object":
                na_fill = interim_modeling_df[col].value_counts().idxmax()
            else:
                na_fill = interim_modeling_df[col].median()

            interim_modeling_df[col] = interim_modeling_df[col].fillna(value = na_fill)
    
    invalid_preds = ["school_name", "dbn", "Address (Full)", "City", "Grades", "Grade Low", "Grade High", "SED Code", "Latitude", "Longitude", "Zip"]
    response_vars = ["num_testtakers", "num_offered", "pct_8th_graders_offered", "perc_testtakers", "perc_testtakers_quartile"]
    invalid_preds.extend(response_vars)

    for response in response_vars:
        if response == "perc_testtakers_quartile":
            na_fill_val = 1
        else:
            na_fill_val = 0

        interim_modeling_df[response] = interim_modeling_df[response].fillna(value=na_fill_val)

    interim_pred_df = interim_modeling_df.drop(invalid_preds, axis=1)
    interim_response_df = interim_modeling_df[response_vars]
    return interim_pred_df, interim_response_df