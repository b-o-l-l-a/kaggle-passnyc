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

    cleaned_df.to_csv("{}/cleaned_modeling_data.csv".format(data_dir), index=False)

    return

def get_addtl_columns(df):

    binary_cols = {"econ_need_index_2017_city_diff" : 0}

    for col_to_xfrom, cutoff in binary_cols.items():
        new_col_name = "{}_binary".format(col_to_xfrom)
        df[new_col_name] = np.nan
        df[new_col_name] = np.where(df[col_to_xfrom].astype(float) >= cutoff, True, False)

    perc_testtakers = df["num_testtakers"].astype(float) / df["grade_8_2017_enrollment"].astype(float)
    df["perc_testtakers"] = perc_testtakers
    perc_testtakers_quantiles = perc_testtakers.quantile([0.25, 0.5, 0.75])
    quartile_1_max = perc_testtakers_quantiles[0.25]
    quartile_2_max = perc_testtakers_quantiles[0.5]
    quartile_3_max = perc_testtakers_quantiles[0.75]

    df["perc_testtakers_quartile"] = np.nan
    df["perc_testtakers_quartile"] = np.where(df["perc_testtakers"] <= quartile_1_max, 1, df["perc_testtakers_quartile"])
    df["perc_testtakers_quartile"] = np.where(
        (df["perc_testtakers"] > quartile_1_max) & (df["perc_testtakers"] <= quartile_2_max), 
        2, df["perc_testtakers_quartile"])
    df["perc_testtakers_quartile"] = np.where(
        (df["perc_testtakers"] > quartile_2_max) & (df["perc_testtakers"] <= quartile_3_max), 
        3, df["perc_testtakers_quartile"])
    df["perc_testtakers_quartile"] = np.where(df["perc_testtakers"] > quartile_3_max, 4, df["perc_testtakers_quartile"])

    dist_df = df.apply(get_dist_from_specialized_schools, axis=1)
    df = pd.concat([df, dist_df], axis=1)

    return df

def get_dist_from_specialized_schools(row):
   
    row_long_lat = (float(row['Latitude']), float(row['Longitude']))

    specialized_school_long_lat = {
        "bronx_hs_of_science" : (40.87833, -73.89083),
        "brooklyn_latin_school" : (40.705, -73.9388889),
        "brooklyn_tech_hs" : (40.6888889, -73.9766667),
        "hs_for_math_sci_eng" : (40.8215, -73.9490),
        "hs_of_amer_studies" : (40.8749, -73.8952),
        "queens_hs_for_sci": (40.699, -73.797),
        "staten_island_tech" : (40.5676, -74.1181),
        "stuyvesant_hs" : (40.7178801, -74.0137509)
    }
    

    row = {}
    for specialized_school, specialized_long_lat in specialized_school_long_lat.items():
        row["dist_to_{}".format(specialized_school)] = geopy.distance.vincenty(row_long_lat, specialized_long_lat).miles       

    row["min_dist_to_specialized_school"] = row[min(row, key=row.get)]
    return pd.Series(row)

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

    #use config to pull years. create var that has list of possible scores (i.e., 1-4)
    incoming_state_score_cols = [
        "incoming_ela_level_1_2016_n",
        "incoming_ela_level_1_2017_n",
        "incoming_ela_level_2_2016_n",
        "incoming_ela_level_2_2017_n",
        "incoming_ela_level_3_2016_n",
        "incoming_ela_level_3_2017_n",
        "incoming_ela_level_4_2016_n",
        "incoming_ela_level_4_2017_n",
        "incoming_math_level_1_2016_n",
        "incoming_math_level_1_2017_n",
        "incoming_math_level_2_2016_n",
        "incoming_math_level_2_2017_n",
        "incoming_math_level_3_2016_n",
        "incoming_math_level_3_2017_n",
        "incoming_math_level_4_2016_n",
        "incoming_math_level_4_2017_n"
    ]

    for state_score_col in incoming_state_score_cols:
        df[state_score_col] = df[state_score_col].replace(to_replace="N < 5", value=0)
        df[state_score_col] = df[state_score_col].astype('float')

    df = create_dummy_vars(df)

    return df

def create_dummy_vars(df):

    # might want to handle var City. Grouping uncommon City vals together
    categorical_cols = [
        "Community School?",
        "Rigorous Instruction Rating",
        "Collaborative Teachers Rating",
        "Supportive Environment Rating",
        "Effective School Leadership Rating",
        "Strong Family-Community Ties Rating",
        "Trust Rating",
        "Student Achievement Rating"
    ]

    ref_val_dict = {
        "Rigorous Instruction Rating" : "Meeting Target",
        "Collaborative Teachers Rating" : "Meeting Target",
        "Supportive Environment Rating" : "Meeting Target",
        "Effective School Leadership Rating" : "Meeting Target",
        "Strong Family-Community Ties Rating" : "Meeting Target",
        "Trust Rating" : "Meeting Target",
        "Student Achievement Rating" : "Meeting Target"
    }
    for cat_col in categorical_cols:

        dummy_df = pd.get_dummies(df[cat_col], prefix=cat_col, dummy_na=True)
        dummy_df = dummy_df.astype('float')
        df = pd.concat([df, dummy_df], axis=1)

        drop_val = ref_val_dict.get(cat_col, None)
        if drop_val is None:
            drop_val = df.groupby([cat_col]).size().idxmax()
        
        drop_col = "{}_{}".format(cat_col, drop_val)
        
        df = df.drop(drop_col, axis=1)

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