import pandas as pd
import os
import sys
import numpy as np
def scratch(col_idx):

    col_idx = int(col_idx)
    cwd = os.getcwd()

    school_explorer_df = pd.read_csv("{cwd}/data/2016 School Explorer.csv".format(**locals()))
    shsat_df = pd.read_csv("{cwd}/data/D5 SHSAT Registrations and Testers.csv".format(**locals()))
    school_explorer_df_cols = school_explorer_df.columns.values

    column_cast_obj = {
        "SED Code" : object,
        "District" : object,
        "Zip" : object
    }
    not_useful_cols = ["Adjusted Grade", "New?", "Other Location Code in LCGMS", "Address (Full)"]
    id_cols = ["School Name", "SED Code", "Location Code"]
    disaggregation_vars = ["District","City", "Zip", "Grades", "Community School?"]
    # list of columns that are categorical in school_explorer_df that need to be xformed to float
    perc_transform_vars = ["Percent ELL", "Percent Asian", "Percent Black", "Percent Hispanic" \
                        "Percent Black / Hispanic", "Percent White", "Student Attendance Rate", \
                        "Percent of Students Chronically Absent", "Rigorous Instruction %", \
                        "Collaborative Teachers %", "Supportive Environment %", "Effective School Leadership %", \
                        "Strong Family-Community Ties %", \
                        "Strong Family-Community Ties Rating", "Trust %"
                        ]

    col_name = school_explorer_df_cols[col_idx]
    print("****{}".format(col_name))
    if col_name in column_cast_obj:
        print(school_explorer_df[col_name].astype(column_cast_obj[col_name]).describe())
    else:
        print(school_explorer_df[col_name].describe())
    

def nyt_school_explorer_merge():
    
    cwd = os.getcwd()
    school_explorer_df = pd.read_csv("{cwd}/data/2016 School Explorer.csv".format(**locals()))
    nyt_df = pd.read_csv("{cwd}/data/nyt_article_data.csv".format(**locals()))
    nyt_df[["num_testtakers", "num_offered"]] = nyt_df[["num_testtakers", "num_offered"]].replace(to_replace="—",value=0)
    nyt_df["pct_8th_graders_offered"] = nyt_df["pct_8th_graders_offered"].replace(to_replace="—",value="0%")
    school_explorer_df_cols_to_keep = [
        'School Name',
        'SED Code',
        'Location Code',
        'District',
        'Latitude',
        'Longitude',
        'Address (Full)',
        'City',
        'Zip',
        'Grades',
        'Grade Low',
        'Grade High',
        'Community School?',
        'Economic Need Index',
        'School Income Estimate',
        'Percent ELL',
        'Percent Asian',
        'Percent Black',
        'Percent Hispanic',
        'Percent Black / Hispanic',
        'Percent White',
        'Student Attendance Rate',
        'Percent of Students Chronically Absent',
        'Rigorous Instruction %',
        'Rigorous Instruction Rating',
        'Collaborative Teachers %',
        'Collaborative Teachers Rating',
        'Supportive Environment %',
        'Supportive Environment Rating',
        'Effective School Leadership %',
        'Effective School Leadership Rating',
        'Strong Family-Community Ties %',
        'Strong Family-Community Ties Rating',
        'Trust %',
        'Trust Rating',
        'Student Achievement Rating',
        'Average ELA Proficiency',
        'Average Math Proficiency'
    ]

    trimmed_school_explorer_df = school_explorer_df[school_explorer_df_cols_to_keep]

    output_df = pd.merge(nyt_df ,trimmed_school_explorer_df, left_on="DBN", right_on="Location Code", how="outer")
    output_df['School name'] = np.where(output_df['School name'].isnull(), output_df['School Name'], output_df['School name'])
    output_df['DBN'] = np.where(output_df['DBN'].isnull(), output_df['Location Code'], output_df['DBN'])

    output_df = output_df.drop(['School Name', 'Location Code'], axis=1)
    print("{}/data/nyt_explorer_merged_df.csv".format(cwd))
    output_df.to_csv("{}/data/nyt_explorer_merged_df.csv".format(cwd), index = False)
if __name__ == "__main__":

    nyt_school_explorer_merge()