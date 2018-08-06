import os
import pandas as pd

from create_dummy_vars import create_dummy_vars
from features_utils import clean_percentage_cols, find_grade_8_flg, clean_rows_and_cols, fill_na, cast_as_bool
from get_addtl_columns import get_addtl_columns
from get_socrata_data import get_socrata_data

def features_controller(input_data_dir, output_data_dir):

    output_file_path = "{}/step3_interim_modeling_data.csv".format(output_data_dir)
    
    output_df = pd.read_csv("{}/step2_final_doe_nyt_data.csv".format(input_data_dir))
    
    output_df = clean_percentage_cols(output_df)
    output_df = find_grade_8_flg(output_df)
    output_df = clean_rows_and_cols(output_df)
    output_df = get_addtl_columns(output_df)
    output_df = create_dummy_vars(output_df)
    output_df = get_socrata_data(output_df, input_data_dir)
    output_df = cast_as_bool(output_df)
    output_df = fill_na(output_df)
    output_df.to_csv(output_file_path, index=False)

    print("interim modeling output can be found at: {}".format(output_file_path))
          
    return

# def merge_data(data_dir):
    
#     #doe_file_name = "doe_nonautomated_workflow.csv"
#     doe_file_name = "step2_final_doe_nyt_data.csv"
#     nyt_file_name = "step1_nyt_shsat_article_data.csv"

#     nyt_df = pd.read_csv("{}/{}".format(data_dir, nyt_file_name))
#     doe_df = pd.read_csv("{}/{}".format(data_dir, doe_file_name))

#     nyt_cols_to_keep = [
#         "school_name", "dbn", "num_testtakers", "num_offered", "pct_8th_graders_offered", "pct_black_hispanic"
#     ]
#     nyt_df = nyt_df[nyt_cols_to_keep]
#     merged_df = pd.merge(nyt_df, doe_df, left_on="dbn", right_on="dbn", how="left")
#     merged_df = merged_df.rename(index=str, columns={"school_name_x": "school_name"})
#     merged_df = merged_df.drop(['school_name_y'], axis=1)

#     return merged_df

if __name__ == "__main__":
    
    cwd = os.getcwd()
    input_data_dir = cwd.replace('/src', '') + '/data/external'
    output_data_dir =  cwd.replace('/src', '') + '/data/interim'
    
    features_controller(input_data_dir, output_data_dir)
    