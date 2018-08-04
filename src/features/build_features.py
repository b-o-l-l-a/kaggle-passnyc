import os

def features_controller(input_data_dir, output_data_dir):
    data_dir = "/Users/greg.bolla/Desktop/git-projects/kaggle-passnyc/data"
    merged_df = merge_data(data_dir)

    cleaned_df = clean_percentage_cols(merged_df)
    cleaned_df = find_grade_8_flg(cleaned_df)
    cleaned_df = clean_rows_and_cols(cleaned_df)
    cleaned_df = get_addtl_columns(cleaned_df)
    cleaned_df = create_dummy_vars(cleaned_df)

    cleaned_df.to_csv("{}/cleaned_modeling_data.csv".format(data_dir), index=False)

    return

if __name__ == "__main__":
    
    cwd = os.getcwd()
    
    print(cwd)