import os
import sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model, metrics

from model_utils import get_pred_and_response_dfs, adj_r2_score

def create_single_regressors(input_data_dir, output_data_dir, output_model_summaries_dir):

    interim_modeling_df = pd.read_csv("{}/step3_interim_modeling_data.csv".format(input_data_dir))

    pred_df, response_df, invalid_preds, response_var = get_pred_and_response_dfs(interim_modeling_df)
   
    pred_train, pred_test, response_train, response_test = train_test_split(pred_df, response_df, test_size=0.25, random_state=223)

    single_regression_df = pd.DataFrame()

    for col in pred_train.columns.values:
        if col in invalid_preds:
            continue
        else: 
            categorical = True if pred_train[col].dtype == "object" else False
            pred_rows = get_single_regressor_model(col, pred_train, response_train, pred_test, response_test, response_var, categorical)
            single_regression_df = single_regression_df.append(pred_rows, ignore_index=True)
            
    single_regression_df_cols = ["model", "categorical", "model_r2", "model_adj_r2", "median_absolute_error", "pred_col", "pred_coef"]
    single_regression_df = single_regression_df[single_regression_df_cols]
    output_file_path = "{}/single_regressor_summary.csv".format(output_model_summaries_dir)
    print("dropping single regression CSV to {}".format(output_file_path))
    
    single_regression_df.to_csv(output_file_path, index=False)
    
def get_single_regressor_model(col_name, pred_train, response_train, pred_test, response_test, response_var, categorical_bool):
    model_rows = []
    
    col_list = pred_train.columns.values
    
    if categorical_bool == True:
        col_vars = [var for var in col_list if "{}_".format(col_name) in var]
    else:
        col_vars = [col_name]
    x_train_df = pred_train[col_vars]
    x_test_df = pred_test[col_vars]
    x_model = linear_model.LinearRegression()
    x_results = x_model.fit(x_train_df, response_train[response_var])

    y_predicted_test = x_results.predict(x_test_df)
    med_absolute_error = metrics.median_absolute_error(response_test[response_var], y_predicted_test)
    r2 = metrics.r2_score(response_test[response_var],y_predicted_test)
    adj_r2 = adj_r2_score(x_results, response_test[response_var],y_predicted_test)

    coef_dict = {}
    model_rows = []
    for idx, col in enumerate(x_train_df.columns.values):
        coef_dict[col] = x_results.coef_[idx]
        model_row = {}
        model_row['model'] = col_name
        pred_coef = x_results.coef_[idx]
        model_row['model_r2'] = r2
        model_row['model_adj_r2'] = adj_r2
        model_row['median_absolute_error'] = med_absolute_error
        model_row['pred_col'] = col if categorical_bool == True else None
        model_row['pred_coef'] = pred_coef
        model_row['categorical'] = categorical_bool
        model_rows.append(model_row)

    return model_rows
if __name__ == "__main__":
    
    cwd = os.getcwd()
    input_data_dir =  cwd.replace('/src', '') + '/data/interim'
    output_data_dir = cwd.replace('/src', '') + '/data/processed'
    output_model_summaries_dir =  cwd.replace('/src', '') + '/models'
    create_single_regressors(input_data_dir, output_data_dir, output_model_summaries_dir)