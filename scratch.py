import pandas as pd
import os

def scratch():

    cwd = os.getcwd()

    school_explorer_df = pd.read_csv("{cwd}/data/2016 School Explorer.csv".format(**locals()))
    shsat_df = pd.read_csv("{cwd}/data/D5 SHSAT Registrations and Testers.csv".format(**locals()))

    print(school_explorer_df.head())
    print(shsat_df.head())

if __name__ == "__main__":
    scratch()