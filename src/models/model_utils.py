# from sklearn import metrics

def adj_r2_score(lm, y, y_pred):
    adj_r2 = 1 - float(len(y)-1)/(len(y)-len(lm.coef_)-1)*(1 - metrics.r2_score(y,y_pred))
    return adj_r2

def get_pred_and_response_dfs(df):

    invalid_preds = ["school_name", "dbn", "Address (Full)", "City", "Grades", "Grade Low", "Grade High", \
    "SED Code", "Latitude", "Longitude", "Zip"]
    response_vars = ["num_testtakers", "num_offered", "pct_8th_graders_offered", "perc_testtakers", "perc_testtakers_quartile"]
    response_var = "perc_testtakers"
    
    # incl dbn and school_name for convenience and to id each row
    response_df_cols = ["dbn", "school_name", response_var]
    
    response_df = df[response_df_cols]
    pred_df = df.drop(response_df_cols, axis=1)
    
    return pred_df, response_df, invalid_preds