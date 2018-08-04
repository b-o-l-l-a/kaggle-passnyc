import os
import sys
import pandas as pd
import warnings

from nyt_shsat_article import nyt_web_scrape
from nyc_dept_of_ed import dept_of_ed_web_scrape

def web_scrape_controller(start_idx = 0, debug_flg = False):

    cwd = os.getcwd()
    print("****cwd: {}".format(cwd))
    data_drop_dir = '{}/data/external'.format(cwd.replace('/src', ''))
    print(data_drop_dir)
    nyt_shsat_df = nyt_web_scrape(data_drop_dir)
    dept_of_ed_df = dept_of_ed_web_scrape(nyt_shsat_df, data_drop_dir, start_idx, debug_flg)

if __name__ == "__main__":
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if len(sys.argv) > 1:
            start_idx = sys.argv[1]
            debug_flg = True
            web_scrape_controller(start_idx, debug_flg)

        else:
            web_scrape_controller()
    