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

    
    print("-- dropping NYT article CSV to {}".format(csv_drop_path))
    output_df.to_csv(csv_drop_path, index = False)

    return output_df