import pandas as pd
import os
import sys

def scratch():

    cwd = os.getcwd()

    school_explorer_df = pd.read_csv("{cwd}/data/2016 School Explorer.csv".format(**locals()))
    shsat_df = pd.read_csv("{cwd}/data/D5 SHSAT Registrations and Testers.csv".format(**locals()))

    shsat_df["% eligible registered"] = shsat_df["Number of students who registered for the SHSAT"] / shsat_df["Enrollment on 10/31"]
    shsat_df["% eligible to take test"] = shsat_df["Number of students who took the SHSAT"] / shsat_df["Enrollment on 10/31"]
    shsat_df_2016 = shsat_df[shsat_df["Year of SHST"] == 2016]
    #print(shsat_df_2016[["School name", "% eligible to take test"]].sort_values("% eligible to take test", ascending=False).head())

    xformed_df_cols = ["School Name", "year", 
        "8th_grade_enrollment", "8th_grade_registered", "8th_grade_testtakers",
        "9th_grade_enrollment", "9th_grade_registered", "9th_grade_testtakers"    
    ]
    shsat_output_df = pd.DataFrame(columns=xformed_df_cols)
    for idx, row in shsat_df_2016.iterrows():
        school = row["School name"]
        grade_level = row["Grade level"]
        enrollment_count = row["Enrollment on 10/31"]
        num_registered = row["Number of students who registered for the SHSAT"]
        num_testtakers = row["Number of students who took the SHSAT"]

        if shsat_output_df["School Name"].isin([school]).any():
            shsat_output_df.loc[\
                shsat_output_df["School Name"] == school, \
                "{}th_grade_enrollment".format(grade_level)] = enrollment_count
            shsat_output_df.loc[\
                shsat_output_df["School Name"] == school, \
                "{}th_grade_registered".format(grade_level)] = num_registered
            shsat_output_df.loc[\
                shsat_output_df["School Name"] == school, \
                "{}th_grade_testtakers".format(grade_level)] = num_testtakers
            
        else:
            new_row = {}
            new_row["School Name"] = school
            new_row["year"] = 2016
            new_row["{}th_grade_enrollment".format(grade_level)] = enrollment_count
            new_row["{}th_grade_registered".format(grade_level)] = num_registered
            new_row["{}th_grade_testtakers".format(grade_level)] = num_testtakers
            shsat_output_df = shsat_output_df.append(new_row, ignore_index = True)


    na_fill_w_0_cols = ["8th_grade_enrollment", "8th_grade_registered", "8th_grade_testtakers",
        "9th_grade_enrollment", "9th_grade_registered", "9th_grade_testtakers"] 
    shsat_output_df[na_fill_w_0_cols] = shsat_output_df[na_fill_w_0_cols].fillna(0)

    shsat_output_df["possible_testtaker_count"] = shsat_output_df["8th_grade_enrollment"] + shsat_output_df["9th_grade_enrollment"]
    shsat_output_df["num_registered"] = shsat_output_df["8th_grade_registered"] + shsat_output_df["9th_grade_registered"]
    shsat_output_df["num_testtakers"] = shsat_output_df["8th_grade_testtakers"] + shsat_output_df["9th_grade_testtakers"]

    shsat_output_df["School Name"] = shsat_output_df["School Name"].str.upper()
    output_df = pd.merge(school_explorer_df, shsat_output_df, on="School Name", how="left")
    print(output_df[["School Name", "num_testtakers"]][output_df["District"] == 5])
    print(shsat_output_df[["School Name", "num_testtakers"]])
    return output_df


if __name__ == "__main__":
    cwd = os.getcwd()
    print(cwd)
    merged_df = scratch()
    merged_df.to_csv("{}/data/merged_df.csv".format(cwd), index = False)