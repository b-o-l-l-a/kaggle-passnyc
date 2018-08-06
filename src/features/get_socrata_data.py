import os
import pandas as pd
import numpy as np

def get_socrata_data(df, data_dir):
    
    print("--getting socrates data to incorporate into modeling")
    df = get_disc_funding_by_zip(data_dir, df)
    df = get_school_safety_by_dbn(data_dir, df)
    
    return df

def get_school_safety_by_dbn(data_dir, df):
    
    school_safety_filename = '2010-2016-school-safety-report.csv'
    school_safety_df = pd.read_csv("{}/{}".format(data_dir, school_safety_filename))
    consolidated_loc_df = school_safety_df[school_safety_df["DBN"].isnull()]
    
    cols_to_fill = ["Major N", "Oth N", "NoCrim N", "Prop N", "Vio N", 
        "AvgOfMajor N", "AvgOfOth N", "AvgOfNoCrim N", "AvgOfProp N", "AvgOfVio N"] 
    
    consolidated_locations = consolidated_loc_df["Building Name"].unique()
    school_yrs = consolidated_loc_df["School Year"].unique()
    
    consolidated_loc_data = {}
    for location in consolidated_locations:
        consolidated_loc_data[location] = {}
        loc_df = consolidated_loc_df[consolidated_loc_df["Building Name"] == location]

        for year in school_yrs:    
            loc_yr_row = loc_df[loc_df["School Year"] == year]  
            if len(loc_yr_row) == 0:
                # no data for that consolidated loc in that particular school yr
                continue
            elif len(loc_yr_row) > 1:
                raise ValueError("duplicate data found for {} / {}".format(location, year))
            loc_yr_dict = get_loc_yr_data(loc_yr_row, cols_to_fill)
            consolidated_loc_data[location][year] = loc_yr_dict    
    dbn_crimes_df = pd.DataFrame()
    school_safety_df.head()

    for idx, row in school_safety_df.iterrows():

        dbn = row['DBN']
        dbn_nan_flg = isinstance(dbn, float) and np.isnan(dbn)
        building_name = row['Building Name']
        bldg_nan_flg = isinstance(building_name, float) and np.isnan(building_name)
        if dbn_nan_flg == False and bldg_nan_flg == False:
            dbn = dbn.strip()
            school_yr = row['School Year']      
            if building_name not in consolidated_loc_data.keys():
                # no data for consolidated location
                continue
            if school_yr not in consolidated_loc_data[building_name].keys():
                # no data for consolidated location in that school year
                continue
            loc_yr_data = consolidated_loc_data[building_name][school_yr]

            #print([row[col] for col in cols_to_fill])
            for col in cols_to_fill:
                row[col] = loc_yr_data[col]

        dbn_crimes_df = dbn_crimes_df.append(row)
    dbn_crimes_df = dbn_crimes_df[~dbn_crimes_df["DBN"].isnull()]
    dbn_crimes_df = dbn_crimes_df.groupby(['DBN'])[cols_to_fill].agg('sum').reset_index()

    output_df = pd.merge(df, dbn_crimes_df, left_on='dbn', right_on='DBN', how='left').drop("DBN",axis=1)
    
    for col in cols_to_fill:
        col_median = output_df[col].median()
        output_df[col] = output_df[col].fillna(value=col_median)

    numerator_cols = ["Major N", "Oth N", "NoCrim N", "Prop N", "Vio N"]
    for numerator in numerator_cols:
        denominator = "AvgOf{}".format(numerator)
        new_col_name = "{}_proportion".format(numerator)
        output_df[new_col_name] = output_df[numerator].astype(float) / output_df[denominator].astype(float)

    return output_df
    
def get_loc_yr_data(row, cols_to_fill):
    
    row_dict = {}
    for col in cols_to_fill:
        row_dict[col] = row[col].values[0]

    return row_dict

def get_disc_funding_by_zip(data_dir, df):
    
    discretionary_funding_filename = 'new-york-city-council-discretionary-funding-2009-2013.csv'
    disc_fund_df = pd.read_csv("{}/{}".format(data_dir, discretionary_funding_filename))
    
    disc_fund_df = disc_fund_df[disc_fund_df["Status "].isin(["Cleared", "Pending"])]
    disc_fund_df = disc_fund_df[disc_fund_df["Postcode"].notnull()]
    disc_fund_df["zip"] = disc_fund_df.apply(clean_zip, axis=1)

    disc_fund_df = disc_fund_df[disc_fund_df['zip'].apply(lambda x: str(x).isdigit())]
    disc_fund_df["zip"] = disc_fund_df["zip"].astype(int)
    disc_fund_df = disc_fund_df[disc_fund_df['zip'].apply(lambda x: len(str(x)) == 5)]
    
    disc_funds_by_zip = disc_fund_df.groupby(['zip'])['Amount '].agg('sum').to_frame().reset_index()
    disc_funds_by_zip.columns = ["zip", "discretionary_funding"]
    disc_funds_by_zip["discretionary_funding"] = disc_funds_by_zip["discretionary_funding"].astype(float)
    
    output_df = pd.merge(df, disc_funds_by_zip, left_on='Zip', right_on='zip', how='left').drop("zip",axis=1)
    
    return output_df

def clean_zip(row):

    raw_zip = row["Postcode"]
    cleaned_zip = raw_zip.split("-")[0]
    return cleaned_zip