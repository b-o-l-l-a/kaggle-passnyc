import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

def nyt_web_scrape(data_dir):

    print("\nscraping NYT article with SHSAT stats")
    nyt_schools_url = "https://www.nytimes.com/interactive/2018/06/29/nyregion/nyc-high-schools-middle-schools-shsat-students.html"
    csv_drop_path = "{}/nyt_shsat_article_data.csv".format(data_dir)
    
    schools_html = requests.get(nyt_schools_url, verify=False).content
    schools_html = schools_html.decode("utf-8")
    schools_soup = BeautifulSoup(re.sub("<!--|-->","", schools_html), "lxml") 

    schools_table = schools_soup.find(class_="g-schools-table-container").table.tbody
    school_rows = schools_table.findAll('tr')

    nyt_article_cols = [
        "school_name",
        "dbn",
        "num_testtakers",
        "num_offered",
        "pct_8th_graders_offered",
        "pct_black_hispanic"
    ]
    output_df = pd.DataFrame(columns = nyt_article_cols)
    
    for school in school_rows:
        
        school_dict = {}        
        school_name = school['data-name']
        dbn = school['data-dbn']
        school_dict['school_name'] = school_name
        school_dict['dbn'] = dbn

        school_data = school.findAll('td')

        for td in school_data:

            school_stat = td['class']

            if "g-testers" in school_stat :
                school_dict['num_testtakers'] = td.string
            elif "g-offers" in school_stat:
                school_dict['num_offered'] = td.string
            elif "g-offers-per-student" in school_stat:
                school_dict['pct_8th_graders_offered'] = td.string
            elif "g-pct" in school_stat:
                school_dict['pct_black_hispanic'] = td.string

        output_df = output_df.append(school_dict, ignore_index = True)

    
    merged_df = merge_w_explorer_data(output_df, data_dir)
    print("-- dropping NYT article CSV to {}".format(csv_drop_path))
    merged_df.to_csv(csv_drop_path, index = False)

    return merged_df

def merge_w_explorer_data(nyt_df, data_dir):

    school_explorer_df = pd.read_csv("{}/archive/2016 School Explorer.csv".format(data_dir))
    
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
    
    merged_df = pd.merge(nyt_df, trimmed_school_explorer_df, left_on="dbn", right_on="Location Code", how="outer")
    
    # combine school_name column from nyt and school explorer data
    merged_df['school_name'] = np.where(merged_df['school_name'].isnull(), merged_df['School Name'], merged_df['school_name'])
    merged_df['dbn'] = np.where(merged_df['dbn'].isnull(), merged_df['Location Code'], merged_df['dbn'])

    merged_df = merged_df.drop(['School Name', 'Location Code'], axis=1)

    return merged_df