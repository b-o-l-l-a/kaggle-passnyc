import os
import sys

from nyt_shsat_article import nyt_web_scrape
from nyc_dept_of_ed import dept_of_ed_web_scrape

def web_scrape_controller(start_idx = 0, debug_flg = False):

    data_dir = os.getcwd().replace('/web_scraping', '') + '/data'

    nyt_shsat_df = nyt_web_scrape(data_dir)
    dept_of_ed_df = dept_of_ed_web_scrape(nyt_shsat_df, data_dir, start_idx, debug_flg)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        start_idx = sys.argv[1]
        debug_flg = True
        web_scrape_controller(start_idx, debug_flg)

    else:
        web_scrape_controller()
    
    

