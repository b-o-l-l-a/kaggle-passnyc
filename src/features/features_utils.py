import pandas as pd
import re

def cast_as_bool(df):
    
    # sorry...this is messy. just checks to see if there are columns w/data type of float and 1,0
    # then casts as bool    
    for col in df.columns.values:
        if df[col].dtype == "float64":
            if len(df[col].unique()) == 2 \
                and 1 in df[col].unique() \
                and 0 in df[col].unique():

                df[col] = df[col].astype(bool)
            
    return df

def fill_na(df):

    response_vars = ["num_testtakers", "num_offered", "pct_8th_graders_offered", "perc_testtakers", "perc_testtakers_quartile"]
    for response in response_vars:
        if response == "perc_testtakers_quartile":
            na_fill_val = 1
        else:
            na_fill_val = 0

        df[response] = df[response].fillna(value=na_fill_val)    
    
    nobs = float(len(df))
    
    for col in df.columns.values:

        num_nulls = float(df[col].isnull().sum())

        if num_nulls / nobs > .1 or len(df[col].unique()) == 1:

            df = df.drop(col, axis = 1)

        elif num_nulls > 0:
            if df[col].dtype == "object":
                na_fill = df[col].value_counts().idxmax()
            else:
                na_fill = df[col].median()

            df[col] = df[col].fillna(value = na_fill)
    
    #invalid_preds = ["school_name", "dbn", "Address (Full)", "City", "Grades", "Grade Low", "Grade High", "SED Code", "Latitude", "Longitude", "Zip"]
    
    #invalid_preds.extend(response_vars)
#     interim_pred_df = interim_modeling_df.drop(invalid_preds, axis=1)
#     interim_response_df = interim_modeling_df[response_vars]
    return df

def transform_pct(col_string):
    
    if pd.isnull(col_string):
        col_val = col_string
    else:
        result = re.search('(.*)%', col_string)
        col_val = float(result.group(1))
        col_val = col_val / 100

    return col_val

def transform_pct_diff(col_string):

    #test = col_string.extract('^(\+|-)+(.*)%')
    if pd.isnull(col_string):
        col_val = col_string
    else:    
        result = re.search('^(\+|-)+(.*)%', col_string)

        sign = result.group(1) 
        col_val = float(result.group(2))
        positive = True if sign == '+' else False
        col_val = -1 * col_val if positive == False else col_val
        col_val = col_val / 100

    return col_val

def clean_percentage_cols(modeling_df):

    modeling_df_cols = modeling_df.columns.values

    for col in modeling_df_cols:
        df_col = modeling_df[col]

        clean_pct_flg = True if (df_col.dtype == object) and (df_col.str.contains('%').any()) else False
        if clean_pct_flg:

            # reason why escape char \ is used is bc of regex underneath the hood of Series.str.contains
            perc_diff_flg = True if (df_col.str.contains('\+').any()) and (df_col.str.contains('-').any()) else False
            
            if perc_diff_flg == True:
                df_col = df_col.apply(transform_pct_diff)
            else:
                df_col = df_col.apply(transform_pct)
        modeling_df[col] = df_col
    return modeling_df

def find_grade_8_flg(df):

    bool_series = df.apply(lambda row: True if '8' in str(row['Grades']) else False, axis=1)
    df['grade_8_flg'] = bool_series

    return df

def clean_rows_and_cols(df):

    # these schools were established in last year or two, and do not yet have 8th graders
    dbns_to_remove = ["15K839", "03M291", "84X492", "84X460", "28Q358"]
    df = df[~df['dbn'].isin(dbns_to_remove)]
    
    #TODO: use config to pull years and create incoming_state_score_cols in a better way
    incoming_state_score_cols = [
        "incoming_ela_level_1_2017_n",
        "incoming_ela_level_2_2017_n",
        "incoming_ela_level_3_2017_n",
        "incoming_ela_level_4_2017_n",
        "incoming_math_level_1_2017_n",
        "incoming_math_level_2_2017_n",
        "incoming_math_level_3_2017_n",
        "incoming_math_level_4_2017_n"
    ]

    for state_score_col in incoming_state_score_cols:
        df[state_score_col] = df[state_score_col].replace(to_replace="N < 5", value=0)
        df[state_score_col] = df[state_score_col].astype('float')

    nobs = float(len(df))

    # remove schools that don't have 8th graders taking the SHSAT
    df = df[df["grade_8_flg"] == True]

    # remove columns with > 25% nulls
    for col_name in df.columns.values:
        
        col_nulls = float(df[col_name].isnull().sum())
        perc_nulls = col_nulls / nobs
        
        if perc_nulls > 0.25:
            df = df.drop(col_name, axis=1)

    # remove schools that don't have 8th grade enrollment    
    df = df.dropna(axis=0, subset=["grade_8_2017_enrollment"])

    return df