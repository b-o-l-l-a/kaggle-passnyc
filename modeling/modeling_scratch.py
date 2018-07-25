import pandas as pd
import re
import numpy as np

def modeling_scratch():
    data_dir = "/Users/greg.bolla/Desktop/git-projects/kaggle-passnyc/data"
    merged_df = merge_data(data_dir)

    cleaned_df = clean_percentage_cols(merged_df)
    cleaned_df = find_grade_8_flg(cleaned_df)
    #cleaned_df = get_addtl_columns(cleaned_df)
    cleaned_df = clean_rows_and_cols(cleaned_df)

    cleaned_df.to_csv("{}/cleaned_modeling_data.csv".format(data_dir), index=False)

    return

def clean_rows_and_cols(df):

    # these schools were established in last year or two, and do not yet have 8th graders
    dbns_to_remove = ["15K839", "03M291", "84X492", "84X460", "28Q358"]
    df = df[~df['dbn'].isin(dbns_to_remove)]

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

def find_grade_8_flg(df):

    bool_series = df.apply(lambda row: True if '8' in str(row['Grades']) else False, axis=1)
    df['grade_8_flg'] = bool_series
    
    return df

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

def merge_data(data_dir):
    
    doe_file_name = "test_df.csv"
    nyt_file_name = "nyt_shsat_article_data.csv"

    nyt_df = pd.read_csv("{}/{}".format(data_dir, nyt_file_name))
    doe_df = pd.read_csv("{}/archive/{}".format(data_dir, doe_file_name))

    merged_df = pd.merge(nyt_df, doe_df, left_on="dbn", right_on="dbn", how="left")
    merged_df = merged_df.rename(index=str, columns={"school_name_x": "school_name"})
    merged_df = merged_df.drop(['school_name_y'], axis=1)
    #merged_df.to_csv("{}/archive/modeling_data.csv".format(data_dir), index=False)

    return merged_df

if __name__ == "__main__":
    modeling_scratch()