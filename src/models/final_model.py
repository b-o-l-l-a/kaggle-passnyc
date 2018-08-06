import os
import sklearn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import linear_model, metrics, preprocessing

from model_utils import get_pred_and_response_dfs, adj_r2_score

def create_final_model(input_data_dir, output_data_dir, output_model_summaries_dir):

    interim_modeling_df = pd.read_csv("{}/step3_interim_modeling_data.csv".format(input_data_dir))

    pred_df, response_df, invalid_preds, response_var = get_pred_and_response_dfs(interim_modeling_df)
    
    model_1_pred_train, model_1_pred_test, model_1_response_train, model_1_response_test = \
    train_test_split(pred_df, response_df, test_size=0.5, random_state=223)
    
    model_2_pred_train = model_1_pred_test
    model_2_pred_test = model_1_pred_train
    model_2_response_train = model_1_response_test
    model_2_response_test = model_1_response_train
    
    final_preds = [
    #"school_name", "dbn", # only incl these two for convenience in ID'ing rows
    "Average ELA Proficiency", 
    "pct_math_level_3_or_4_2017_city_diff", 
    "sa_attendance_90plus_2017", 
    "pct_8th_graders_w_hs_credit_2017_city_diff",
    "min_dist_to_big_three"
#     "Collaborative Teachers Rating_Approaching Target",
#     "Collaborative Teachers Rating_Exceeding Target",
#     "Collaborative Teachers Rating_Not Meeting Target",
#     "Collaborative Teachers Rating_nan",
#     "Major N_proportion"
]
    model_1_train_pred_df = model_1_pred_train[final_preds]
    model_1_test_pred_df = model_1_pred_test[final_preds]
    
    model_2_train_pred_df = model_2_pred_train[final_preds]
    model_2_test_pred_df = model_2_pred_test[final_preds]
    
    stdized_model_1_train, stdized_model_1_test = standardize_cols(model_1_train_pred_df, model_1_test_pred_df)
    stdized_model_2_train, stdized_model_2_test = standardize_cols(model_2_train_pred_df, model_2_test_pred_df)
    
    model_1 = linear_model.LinearRegression().fit(stdized_model_1_train, model_1_response_train[response_var])
    model_1_test_predicted = model_1.predict(stdized_model_1_test)
    model_1_response_test["predicted_perc_testtakers"] = model_1_test_predicted
    model_1_coefficients = pd.concat([pd.DataFrame(stdized_model_1_train.columns),pd.DataFrame(np.transpose(model_1.coef_))], axis = 1)
    model_1_coefficients.columns = ["model_1_pred_name", "model_1_coef"]

    model_2 = linear_model.LinearRegression().fit(stdized_model_2_train, model_2_response_train[response_var])
    model_2_test_predicted = model_2.predict(stdized_model_2_test)
    model_2_response_test["predicted_perc_testtakers"] = model_2_test_predicted
    model_2_coefficients = pd.concat([pd.DataFrame(stdized_model_2_train.columns),pd.DataFrame(np.transpose(model_2.coef_))], axis = 1)
    model_2_coefficients.columns = ["model_2_pred_name", "model_2_coef"]
    
    final_test_set =  pd.concat([model_1_response_test, model_2_response_test])

    final_test_set.to_csv("{}/predictions_by_school.csv".format(output_model_summaries_dir), index = False)
    model_1_coefficients.to_csv("{}/model_1_coefficients.csv".format(output_model_summaries_dir), index = False)
    model_2_coefficients.to_csv("{}/model_2_coefficients.csv".format(output_model_summaries_dir), index = False)
    
    final_r2 = metrics.r2_score(final_test_set["perc_testtakers"], final_test_set["predicted_perc_testtakers"])
    final_median_abs_err = metrics.median_absolute_error(final_test_set["perc_testtakers"], final_test_set["predicted_perc_testtakers"])
    
    print("\n\nmodel_1_coefficients: ")
    print(model_1_coefficients)
    print("\nmodel_2_coefficients: ")
    print(model_2_coefficients)
    print("\n\n** r2 of entire dataset: {}".format(final_r2))
    print("** median_absolute_error of entire dataset: {}".format(final_median_abs_err))
    
    print("\n\ndropped output to folder: {}".format(output_model_summaries_dir))
    
    
def standardize_cols(train_df, test_df):
    
    standardized_train_df = train_df
    standardized_test_df = test_df
    for pred_col in train_df.columns.values:
        if train_df[pred_col].dtype == "float64":
            scaler = preprocessing.StandardScaler().fit(standardized_train_df[[pred_col]])
            standardized_train_df["{}_stdized".format(pred_col)] = scaler.transform(standardized_train_df[[pred_col]])
            standardized_test_df["{}_stdized".format(pred_col)] = scaler.transform(standardized_test_df[[pred_col]])
            standardized_train_df = standardized_train_df.drop(pred_col, axis=1)
            standardized_test_df = standardized_test_df.drop(pred_col, axis=1)
    return standardized_train_df, standardized_test_df

if __name__ == "__main__":
    
    cwd = os.getcwd()
    input_data_dir =  cwd.replace('/src', '') + '/data/interim'
    output_data_dir = cwd.replace('/src', '') + '/data/processed'
    output_model_summaries_dir =  cwd.replace('/src', '') + '/models'
    create_final_model(input_data_dir, output_data_dir, output_model_summaries_dir)