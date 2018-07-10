import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
from selenium import webdriver
import time
import math

wait_time_after_click = 0.25
wait_time_after_exception = 30

def dept_of_ed_web_scrape(school_df, data_dir, start_idx = 0 , debug_flg = False):

    if debug_flg == False:
        output_df = pd.DataFrame()
    else:
        output_df = pd.read_csv("{data_dir}/in_flight_doe_data.csv".format(**locals()))

    DoE_base_url = "https://tools.nycenet.edu/guide/{year}/#dbn={dbn}&report_type=EMS"

    for idx, school in school_df[start_idx:].iterrows():

        scrape_school_flg = get_scrape_flg(school, DoE_base_url)

        if scrape_school_flg == False: 
            continue
        
        row_dict = get_school_info(school, DoE_base_url)
        output_df = output_df.append(row_dict, ignore_index=True)
        output_df.to_csv("{data_dir}/in_flight_doe_data.csv".format(**locals()),index=False)

def get_school_info(school, DoE_base_url):
    
    years_to_scrape = [2016, 2017]
    school_row_dict = school

    school_name = school['school_name']
    dbn = school['dbn']

    browser = webdriver.Chrome()

    print("-{}".format(school_name))
    for year in years_to_scrape:
        school_url = DoE_base_url.format(year=year, dbn=dbn)
        print("--{}".format(school_url))

        try:
            browser.get(school_url)
            browser.find_element_by_class_name('introjs-skipbutton').click()
        except:
            print("---in except, waiting {} seconds and retrying".format(wait_time_after_exception))
            time.sleep(wait_time_after_exception)
            browser.get(school_url)
            time.sleep(wait_time_after_exception)
            browser.find_element_by_class_name('introjs-skipbutton').click() 
            
        time.sleep(wait_time_after_click)

        school_row_dict = get_student_achievement_stats(browser, school_row_dict)
        school_row_dict = get_student_characteristic_stats(browser, school_row_dict)

    return school_row_dict

def uncollapse_all(browser):
    collapsible_content = browser.find_elements_by_class_name('osp-collapsible-title')
    for x in range(0, len(collapsible_content)):
        if collapsible_content[x].is_displayed():
            collapsible_content[x].click()
            time.sleep(wait_time_after_click)

def get_student_characteristic_stats(browser, school_row_dict):
    
    browser.find_element_by_id('tab-stu-pop').click()
    time.sleep(wait_time_after_click)

    uncollapse_all_content()

    student_characteristic_soup = BeautifulSoup(driver.page_source, "lxml") 

    enrollment_section = student_characteristic_soup.find(id="pop-eot")
    enrollment_content = enrollment_section.find(class_="osp-collapsible-content-wrapper")
    
    for enrollment_grade in enrollment_content.children:
        enrollment_data = enrollment_grade.find(class_="osp-collapsible-title")
        grade = enrollment_data.find(class_="name").string.split("Grade ")[-1]
        try:
            grade = int(grade)
        except ValueError:
            pass
        
        if grade not in [7, 8]:
            continue
        
        class_str = "yr-"
        regex = re.compile(".*({class_str}).*".format(**locals()))
        for child in enrollment_data.children:

            if any('yr-' in string for string in child['class']):
                idx = [i for i, s in enumerate(child['class']) if 'yr-' in s][0]
                class_yr_str = child['class'][idx]
                class_yr = int(class_yr_str.split('yr-')[-1])
                enrollment_yr = year - class_yr

                if enrollment_yr in [2015, 2016, 2017]:
                    school_row_dict["grade_{}_{}_enrollment".format(grade, enrollment_yr)] = child.string

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

        time.sleep(wait_time_after_click)
    return school_row_dict

def get_student_achievement_stats(browser, school_row_dict):
    
    browser.find_element_by_id('tab-stu-achieve').click()
    time.sleep(wait_time_after_click)

    uncollapse_all_content()
    
    sa_soup = BeautifulSoup(browser.page_source, "lxml") 

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

    sa_section = sa_soup.find(id="content-stu-achieve")
    sa_content = sa_section.find(class_="tab-content")

    sa_title = sa_content.find(class_="osp-collapsible-title")
    sa_score = sa_title.find(class_="score").string
    sa_score_dist_diff = sa_title.find(class_="dist").svg.text 
    sa_score_city_diff = sa_title.find(class_="city").svg.text

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

    return school_row_dict

def get_scrape_flg(school_dict, DoE_base_url):

    if isinstance(school_dict['Grades'], float) and math.isnan(school_dict['Grades']):
        return False

    grade_list = school_dict['Grades'].split(",")

    for i, v in enumerate(grade_list): 
        try:
            grade_list[i] = int(v)
        except ValueError:
            grade_list[i] = v
        
    if 8 not in grade_list:
        return False

    else:
        scrape_flg = check_enrollment(school_dict, DoE_base_url)
        return scrape_flg

def check_enrollment(school_dict, DoE_base_url):
    
    dbn = school['dbn']    
    school_url = DoE_base_url.format(year=2017, dbn=dbn)

    browser = webdriver.Chrome()
    browser.get(school_url)
    browser.find_element_by_class_name('introjs-skipbutton').click()

    browser.find_element_by_id('tab-stu-pop').click()
    time.sleep(wait_time_after_click)

    enrollment_elem = browser.find_element_by_id('pop-eot')
    enrollment_elem.find_element_by_class_name('osp-collapsible-title').click()
    time.sleep(wait_time_after_click)

    enrollment_soup = BeautifulSoup(browser.page_source, "lxml") 
    enrollment_content = enrollment_soup.find(id="pop-eot").find(class_="osp-collapsible-content-wrapper")

    scrape_flg = False   

    for enrollment_grade in enrollment_content.children:
        enrollment_data = enrollment_grade.find(class_="osp-collapsible-title")
        grade = enrollment_data.find(class_="name").string.split("Grade ")[-1]

        try:
            grade = int(grade)

            if grade == 8:
                scrape_flg = True

        except ValueError:
            pass
    
    return scrape_flg