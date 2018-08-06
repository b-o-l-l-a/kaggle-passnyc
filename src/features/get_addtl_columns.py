import numpy as np
import pandas as pd
import geopy.distance

def get_addtl_columns(df):

    df = make_continuous_categorical(df)
    df = get_addtl_response_vars(df)
    df['borough'] = df.apply(get_borough, axis=1)

    dist_df = df.apply(get_dist_from_specialized_schools, axis=1)
    df = pd.concat([df, dist_df], axis=1)

    return df

def get_dist_from_specialized_schools(row):
   
    # this only captures distance from feeder school to one of big three specialized schools.
    # however, other specialized schools are incl in specialized_school_long_lat dictionary, if needed
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
    
    big_three_schools = ["bronx_hs_of_science", "brooklyn_tech_hs", "stuyvesant_hs"]

    row = {}
    for specialized_school, specialized_long_lat in specialized_school_long_lat.items():
        if specialized_school in big_three_schools:
            row["dist_to_{}".format(specialized_school)] = geopy.distance.vincenty(row_long_lat, specialized_long_lat).miles       
    row["min_dist_to_big_three"] = row[min(row, key=row.get)]
    return pd.Series(row)

def get_addtl_response_vars(df):
    
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
    
    return df

def make_continuous_categorical(df):
    
    binary_cols = {"econ_need_index_2017_city_diff" : 0}

    for col_to_xfrom, cutoff in binary_cols.items():
        new_col_name = "{}_binary".format(col_to_xfrom)
        df[new_col_name] = np.nan
        df[new_col_name] = np.where(df[col_to_xfrom].astype(float) >= cutoff, True, False)
        
    return df

def get_borough(row):
    
    # taken from NYC dept of health: https://www.health.ny.gov/statistics/cancer/registry/appendix/neighborhoods.htm
    borough_zip_dict = {
        "bronx" : [
            10453, 10457, 10460, 10458, 10467, 10468, 10451, 10452, 10456, \
            10454, 10455, 10459, 10474, 10463, 10471, 10466, 10469, 10470, \
            10475, 10461, 10462, 10464, 10465, 10472, 10473
        ],
        "brooklyn": [
            11212, 11213, 11216, 11233, 11238, 11209, 11214, 11228, 11204, \
            11218, 11219, 11230, 11234, 11236, 11239, 11223, 11224, 11229, \
            11235, 11201, 11205, 11215, 11217, 11231, 11203, 11210, 11225, \
            11226, 11207, 11208, 11211, 11222, 11220, 11232, 11206, 11221, \
            11237
        ],
        "manhattan": [
            10026, 10027, 10030, 10037, 10039, 10001, 10011, 10018, 10019, \
            10020, 10036, 10029, 10035, 10010, 10016, 10017, 10022, 10012, \
            10013, 10014, 10004, 10005, 10006, 10007, 10038, 10280, 10002, \
            10003, 10009, 10021, 10028, 10044, 10065, 10075, 10128, 10023, \
            10024, 10025, 10031, 10032, 10033, 10034, 10040, 10282
        ],
        "queens": [
            11361, 11362, 11363, 11364, 11354, 11355, 11356, 11357, 11358, \
            11359, 11360, 11365, 11366, 11367, 11412, 11423, 11432, 11433, \
            11434, 11435, 11436, 11101, 11102, 11103, 11104, 11105, 11106, \
            11374, 11375, 11379, 11385, 11691, 11692, 11693, 11694, 11695, \
            11697, 11004, 11005, 11411, 11413, 11422, 11426, 11427, 11428, \
            11429, 11414, 11415, 11416, 11417, 11418, 11419, 11420, 11421, \
            11368, 11369, 11370, 11372, 11373, 11377, 11378
        ],
        "staten_island" : [
            10302, 10303, 10310, 10306, 10307, 10308, 10309, 10312, 10301, \
            10304, 10305, 10314, 10311
        ]
    } 

    school_zip = row["Zip"]

    school_boro = None
    for boro, borough_zip_list in borough_zip_dict.items():
        if school_zip in borough_zip_list:
            school_boro = boro
            break
    if school_boro is None:
        school_boro = "other"

    return school_boro