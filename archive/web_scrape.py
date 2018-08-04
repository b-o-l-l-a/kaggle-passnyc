import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time
import math

def nyt_web_scrape():

    nyt_schools_url = "https://www.nytimes.com/interactive/2018/06/29/nyregion/nyc-high-schools-middle-schools-shsat-students.html"
    schools_html = requests.get(nyt_schools_url, verify=False).content
    schools_html = schools_html.decode("utf-8")
    schools_soup = BeautifulSoup(re.sub("<!--|-->","", schools_html), "lxml") 

    schools_table = schools_soup.find(class_="g-schools-table-container").table.tbody
    school_rows = schools_table.findAll('tr')

    nyt_article_cols = [
        "School name",
        "DBN",
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
        school_dict['School name'] = school_name
        school_dict['DBN'] = dbn

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

    csv_drop_path = os.getcwd() + "/data/nyt_article_data.csv"
    print("dropping CSV to {}".format(csv_drop_path))
    output_df.to_csv(csv_drop_path, index = False)

def dept_of_ed_web_scrape():
    cwd = os.getcwd()
    school_df = pd.read_csv("{cwd}/data/nyt_explorer_merged_df.csv".format(**locals()))
    #output_df = pd.DataFrame()
    output_df = pd.read_csv("{cwd}/data/test_df.csv".format(**locals()))
    for idx, school in school_df[1266:].iterrows():
        
        if isinstance(school['Grades'], float):
            if math.isnan(school['Grades']):
                continue

        grade_list = school['Grades'].split(",")
        
        if '08' in grade_list:
            print("index #{}".format(idx))
            row_dict = get_school_info(school)
            output_df = output_df.append(row_dict, ignore_index=True)
            output_df.to_csv("{cwd}/data/test_df.csv".format(**locals()),index=False)

    cols = output_df.columns.values.tolist()
    cols.remove('dbn')
    cols.remove('school_name')
    col_order = ["dbn", "school_name"]
    col_order.extend(cols)
    #print(col_order)
    #school_vals = output_df["school_name"]
    #output_df = output_df.drop(["school_name"], axis=1)
    #output_df.insert(1, "school_name", school_vals)
    output_df[col_order].to_csv("{cwd}/data/test_df.csv".format(**locals()),index=False)
    #print(output_df[["school_name","grade_8_2015_enrollment", "grade_7_2015_enrollment","grade_8_2017_enrollment"]])
def get_school_info(school):
    row_dict = {}

    school_name = school['School name']
    dbn = school['DBN']

    school_row_dict = {
        'school_name' : school_name,
        'dbn' : dbn
    }

    years_to_scrape = [2016, 2017]
    #years_to_scrape = [2017]
    
    DoE_base_url = "https://tools.nycenet.edu/guide/{year}/#dbn={dbn}&report_type=EMS"
    driver = webdriver.Chrome()
    
    for year in years_to_scrape:
        school_url = DoE_base_url.format(year=year, dbn=dbn)
        print("--{}".format(school_url))
        
        #school_yr_html = requests.get(school_url, verify=False).content
        #school_yr_html = school_yr_html.decode("utf-8")
        #school_yr_soup = BeautifulSoup(re.sub("<!--|-->","", school_yr_html), "lxml") 
        #driver.find_element_by_class_name('introjs-overlay').click()
        try:
            driver.get(school_url)
            driver.find_element_by_class_name('introjs-skipbutton').click()
        except:
            print("in except, waiting 20 seconds and retrying")
            time.sleep(20)
            driver.get(school_url)
            time.sleep(20)
            driver.find_element_by_class_name('introjs-skipbutton').click()

        #driver.implicitly_wait(3)
        time.sleep(1)
        #WebDriverWait(driver, 5)

######## STUDENT OUTCOMES
        driver.find_element_by_id('tab-stu-achieve').click()
        time.sleep(1)
        #time.sleep(5)
        collapsible_content = driver.find_elements_by_class_name('osp-collapsible-title')
        for x in range(0, len(collapsible_content)):
            if collapsible_content[x].is_displayed():
                time.sleep(0.25)
                collapsible_content[x].click()
        school_yr_soup = BeautifulSoup(driver.page_source, "lxml") 

        sa_name_dict = {
            "White" : "white",
            "Hispanic" : "hispanic",
            "Asian / Pacific Islander" : "asian_pacific",
            "Black" : "black",
            "Multiracial" : "multiracial",
            "American Indian" : "amer_indian",
            "Math - Average Student Proficiency" : "avg_math_proficiency",
            "Math - Percentage of Students at Level 3 or 4" : "pct_math_level_3_or_4",
            "Percent of 8th Graders Earning HS Credit" : "pct_8th_graders_w_hs_credit"
        }
        sa_section = school_yr_soup.find(id="content-stu-achieve")
        sa_content = sa_section.find(class_="tab-content")
        #sa_content = sa_section.find(class_="osp-collapsible-content-wrapper")
        sa_title = sa_content.find(class_="osp-collapsible-title")
        #print(sa_title.find(class_="name"))
        #sa_name = sa_title.find(class_="name").string
        sa_score = sa_title.find(class_="score").string
        #print("{sa_name} / {sa_score}".format(**locals()))
        sa_score_dist_diff = sa_title.find(class_="dist").svg.text 
        sa_score_city_diff = sa_title.find(class_="city").svg.text

        #print("Student Achievement: {sa_score} / {sa_score_dist_diff} / {sa_score_city_diff}".format(**locals()))
        #print("-------")
        sa_metric_collapsibles = sa_content.find(id="sa-metric-collapsibles")
        for sa_metric in sa_metric_collapsibles.children:
            sa_metric_content = sa_metric.find(class_="osp-collapsible-content-wrapper")

            for sa_stat in sa_metric_content.children:
                sa_title = sa_stat.find(class_="osp-collapsible-title") 
                try:
                    stat_name = sa_title.find(class_="name").div.string
                except AttributeError:
                    stat_name = sa_title.find(class_="name").string

                if stat_name in sa_name_dict.keys():
                    stat_val = sa_title.find(class_="value").string
                    sa_stat_comp_diff = sa_title.find(class_="comp").svg.text 
                    sa_stat_city_diff = sa_title.find(class_="city").svg.text
                    stat_col = sa_name_dict[stat_name]
                    school_row_dict["{}_{}".format(stat_col, year)] = stat_val
                    school_row_dict["{}_{}_comp_diff".format(stat_col, year)] = sa_stat_comp_diff
                    school_row_dict["{}_{}_city_diff".format(stat_col, year)] = sa_stat_city_diff
                    #print("{stat_name} / {stat_val} / {sa_stat_comp_diff} / {sa_stat_city_diff}".format(**locals()))
        
        sa_addtl_info = sa_content.find(id="sa-add-info").find(class_="osp-collapsible-content-wrapper")
        
        sa_attendance_div = sa_addtl_info.find(id="sa-add-info-sg0-m0").find(class_="osp-collapsible-title")
        sa_attendance_name = sa_attendance_div.find(class_="name").div.string
        sa_attendance_val = sa_attendance_div.find(class_="value").string
        try:
            sa_attendance_dist_diff = sa_attendance_div.find(class_="dist").svg.text 
        except AttributeError:
            sa_attendance_dist_diff = sa_attendance_div.find(class_="comp").svg.text 
        sa_attendance_city_diff = sa_attendance_div.find(class_="city").svg.text 
        school_row_dict["sa_attendance_90plus_{}".format(year)] = sa_attendance_val
        school_row_dict["sa_attendance_90plus_{}_dist_diff".format(year)] = sa_attendance_dist_diff
        school_row_dict["sa_attendance_90plus_{}_city_diff".format(year)] = sa_attendance_city_diff
        #print("{sa_attendance_name}: {sa_attendance_val} / {sa_attendance_dist_diff} / {sa_attendance_city_diff}".format(**locals()))
        
        sa_proficiency_scores_by_ethnicity = sa_addtl_info.find(id="sa-add-info-re-nonoverlap").find(class_="cat-demog-collapsibles")
        for sa_proficiency in sa_proficiency_scores_by_ethnicity.children:
            sa_proficiency_row = sa_proficiency.find(class_="osp-collapsible-title")
            ethnicity = sa_proficiency_row.find(class_="name").div.string
            if ethnicity == "Missing or Invalid Data":
                continue
            ethnicity_col_name = sa_name_dict[ethnicity]
            ethnicity_sample_size = sa_proficiency_row.find(class_="n").string
            incoming_ela = sa_proficiency_row.select('div.inc.ela')[0].string
            avg_ela = sa_proficiency_row.select('div.avg.ela')[0].string
            incoming_math = sa_proficiency_row.select('div.inc.mth')[0].string
            avg_math = sa_proficiency_row.select('div.avg.mth')[0].string 
            school_row_dict["{}_{}_num_students".format(ethnicity_col_name, year)] = ethnicity_sample_size
            school_row_dict["{}_{}_incoming_ela".format(ethnicity_col_name, year)] = incoming_ela
            school_row_dict["{}_{}_avg_ela".format(ethnicity_col_name, year)] = avg_ela
            school_row_dict["{}_{}_incoming_math".format(ethnicity_col_name, year)] = incoming_math
            school_row_dict["{}_{}_avg_math".format(ethnicity_col_name, year)] = avg_math
            #print("{ethnicity} ({ethnicity_sample_size}): {incoming_ela} / {avg_ela} / {incoming_math} / {avg_math}".format(**locals()))
        #for sa_addtl_info_child in sa_addtl_info.children:
        #    sa_addtl_info_content = sa_addtl_info_child.find(class_="osp-collapsible-content-wrapper")
        #    for 

        driver.find_element_by_id('tab-stu-pop').click()
        time.sleep(1)
        #time.sleep(5)
        collapsible_content = driver.find_elements_by_class_name('osp-collapsible-title')
        for x in range(0, len(collapsible_content)):
            if collapsible_content[x].is_displayed():
                time.sleep(1)
                collapsible_content[x].click()
        #driver.find_element_by_class_name('osp-collapsible-title').click()
        time.sleep(5)
        #time.sleep(5)
        #school_yr_soup = BeautifulSoup(driver.page_source, "html5lib")
        school_yr_soup = BeautifulSoup(driver.page_source, "lxml") 
        #student_pop = school_yr_soup.find(class_="cat-collapsibles")
##### ENROLLMENT
        enrollment_section = school_yr_soup.find(id="pop-eot")
        enrollment_content = enrollment_section.find(class_="osp-collapsible-content-wrapper")
        
        
        #enrollment = school_yr_soup.select(".osp-collapsible-content-wrapper > .osp-collapsible-title")
        for enrollment_grade in enrollment_content.children:
            enrollment_data = enrollment_grade.find(class_="osp-collapsible-title")
            grade = enrollment_data.find(class_="name").string.split("Grade ")[-1]
            if grade not in ['7', '8']:
                continue
            
            grade = int(grade)
            #print(grade)
            
            class_str = "yr-"
            regex = re.compile(".*({class_str}).*".format(**locals()))
            for child in enrollment_data.children:
                #print("****************")
                if any('yr-' in string for string in child['class']):
                    idx = [i for i, s in enumerate(child['class']) if 'yr-' in s][0]
                    class_yr_str = child['class'][idx]
                    class_yr = int(class_yr_str.split('yr-')[-1])
                    enrollment_yr = year - class_yr
                    if enrollment_yr in [2015, 2016, 2017]:
                        school_row_dict["grade_{}_{}_enrollment".format(grade, enrollment_yr)] = child.string

##########ADDTL SUPPORTS
        addtl_resources_section = school_yr_soup.find(id="pop-hns")
        addtl_resources_content = addtl_resources_section.find(class_="cat-collapsibles")
        addtl_resources_name_dict = {
            "Students in Families Eligible for HRA Assistance" : "pct_hra_assistance",
            "Students in Families with Income Below Federal Poverty Level (Estimated)" : "pct_poverty",
            "Students in Temporary Housing" : "pct_temp_housing",
            "Economic Need Index" : "econ_need_index",
            "Students with Disabilities" : "pct_students_w_disabilities",
            "English Language Learners" : "pct_ell",
            "Avg 5th Grade ELA Rating" : "incoming_avg_5th_grade_ela_rating",
            "Avg 5th Grade Math Rating" : "incoming_avg_5th_grade_math_rating",
            "Math Level 1" : "incoming_math_level_1",
            "Math Level 2" : "incoming_math_level_2",
            "Math Level 3" : "incoming_math_level_3",
            "Math Level 4" : "incoming_math_level_4",
            "ELA Level 1" : "incoming_ela_level_1",
            "ELA Level 2" : "incoming_ela_level_2",
            "ELA Level 3" : "incoming_ela_level_3",
            "ELA Level 4" : "incoming_ela_level_4"
        }
        for addtl_resource_cat in addtl_resources_content.children:
            addtl_resource_cat_data = addtl_resource_cat.find(class_="osp-collapsible-content-wrapper")
        
            cat_section = addtl_resource_cat.find(class_="osp-collapsible-title")
            cat_section_name = cat_section.find(class_="name").div.string
            cat_section_val = cat_section.find(class_="val").string
            cat_section_dist_diff = cat_section.find(class_="dist").svg.text 
            cat_section_city_diff = cat_section.find(class_="city").svg.text 
            stat_col = addtl_resources_name_dict[cat_section_name]
            school_row_dict["{}_{}_val".format(stat_col, year)] = cat_section_val
            school_row_dict["{}_{}_dist_diff".format(stat_col, year)] = cat_section_dist_diff
            school_row_dict["{}_{}_city_diff".format(stat_col, year)] = cat_section_city_diff
            #print("*** {} / val: {} / dist_diff: {} / city_diff: {}".format(cat_section_name, cat_section_val, cat_section_dist_diff, cat_section_city_diff))
            if cat_section_name == "Economic Need Index":
                for subcat in addtl_resource_cat_data.children:
                    subcat_section = subcat.find(class_="osp-collapsible-title")
                    subcat_section_name = subcat_section.find(class_="name").div.string
                    stat_col = addtl_resources_name_dict[subcat_section_name]
                    subcat_section_val = subcat_section.find(class_="val").string
                    subcat_section_dist_diff = subcat_section.find(class_="dist").svg.text 
                    subcat_section_city_diff = subcat_section.find(class_="city").svg.text 
                    school_row_dict["{}_{}_val".format(stat_col, year)] = subcat_section_val
                    school_row_dict["{}_{}_dist_diff".format(stat_col, year)] = subcat_section_dist_diff
                    school_row_dict["{}_{}_city_diff".format(stat_col, year)] = subcat_section_city_diff
                    #print("*** {} / val: {} / dist_diff: {} / city_diff: {}".format(subcat_section_name, subcat_section_val, subcat_section_dist_diff, subcat_section_city_diff))
            #break
#########INCOMING PROFICIENCY
        incoming_proficiency = school_yr_soup.find(id="pop-ipl")
        ipl_content = incoming_proficiency.find(class_="cat-collapsibles")

        for ipl in ipl_content.children:
            ipl_data = ipl.find(class_="osp-collapsible-content-wrapper")
            ipl_section = ipl_data.find(class_="osp-collapsible-title")
            ipl_section_name = ipl_section.find(class_="name").div.string
            ipl_section_val = ipl_section.find(class_="val").string
            ipl_section_dist_diff = ipl_section.find(class_="dist").svg.text 
            ipl_section_city_diff = ipl_section.find(class_="city").svg.text 
            stat_col = addtl_resources_name_dict[ipl_section_name]
            school_row_dict["{}_{}_val".format(stat_col, year)] = ipl_section_val
            school_row_dict["{}_{}_dist_diff".format(stat_col, year)] = ipl_section_dist_diff
            school_row_dict["{}_{}_city_diff".format(stat_col, year)] = ipl_section_city_diff
            #print("******{ipl_section_name} : {ipl_section_val} / {ipl_section_dist_diff} / {ipl_section_city_diff}".format(**locals()))
            if ipl_section_name in ["Avg 5th Grade ELA Rating", "Avg 5th Grade Math Rating"]:
                if ipl_section_name == "Avg 5th Grade Math Rating":
                    stat_col_prepend = "Math"
                elif ipl_section_name == "Avg 5th Grade ELA Rating":
                    stat_col_prepend = "ELA"
                ipl_collapsible_children = ipl_data.find(class_="osp-collapsible-content-wrapper")
                for ipl_sub in ipl_collapsible_children.children:
                    ipl_subsection = ipl_sub.find(class_="osp-collapsible-title")
                    ipl_subsection_name = ipl_subsection.find(class_="name").div.string
                    ipl_subsection_val = ipl_subsection.find(class_="val").string
                    ipl_subsection_size = ipl_subsection.find(class_="n").string
                    ipl_subsection_dist_diff = ipl_subsection.find(class_="dist").svg.text 
                    ipl_subsection_city_diff = ipl_subsection.find(class_="city").svg.text
                    stat_col = addtl_resources_name_dict["{} {}".format(stat_col_prepend, ipl_subsection_name)]
                    school_row_dict["{}_{}_val".format(stat_col, year)] = ipl_subsection_val
                    school_row_dict["{}_{}_n".format(stat_col, year)] = ipl_subsection_size
                    school_row_dict["{}_{}_dist_diff".format(stat_col, year)] = ipl_subsection_dist_diff
                    school_row_dict["{}_{}_city_diff".format(stat_col, year)] = ipl_subsection_city_diff
                    #print("---{ipl_subsection_name} ({ipl_subsection_size}): {ipl_subsection_val} / {ipl_subsection_dist_diff} / {ipl_subsection_city_diff}".format(**locals()))
        time.sleep(1)



        time.sleep(1)


    return school_row_dict
def get_student_pop_data():
    return

def get_student_outcomes_data():
    return

if __name__ == "__main__":

    dept_of_ed_web_scrape()