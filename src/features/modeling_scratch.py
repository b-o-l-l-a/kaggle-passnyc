import pandas as pd
import re
import numpy as np
import geopy.distance

def modeling_scratch():
    data_dir = "/Users/greg.bolla/Desktop/git-projects/kaggle-passnyc/data"
    merged_df = merge_data(data_dir)

    cleaned_df = clean_percentage_cols(merged_df)
    cleaned_df = find_grade_8_flg(cleaned_df)
    cleaned_df = clean_rows_and_cols(cleaned_df)
    cleaned_df = get_addtl_columns(cleaned_df)
    cleaned_df = create_dummy_vars(cleaned_df)

    cleaned_df.to_csv("{}/cleaned_modeling_data.csv".format(data_dir), index=False)

    return

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