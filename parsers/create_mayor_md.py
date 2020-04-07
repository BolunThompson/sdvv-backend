from pandas import read_csv
from os import path, makedirs, chdir
from math import isnan


chdir("..")
SD_CANDIDATES = read_csv("downloads/csv/sd_candidates.csv")
FILE_PATH = "build/_office_elections/sandiego/2020-11-03/mayor.md"


def remove_NaN(dictionary):
    '''
    Takes a dictionary and replaces NaN values with empty strings
    '''
    for key in dictionary:
        try:
            if isnan(dictionary[key]):
                dictionary[key] = ""
        except TypeError:
            pass


candidate_dicts = SD_CANDIDATES.transpose().to_dict()
directory = path.split(FILE_PATH)[0]
if not path.exists(directory):
    makedirs(directory)
with open(FILE_PATH, mode="w") as f:
    for candidate_dict in candidate_dicts.values():
        remove_NaN(candidate_dict)
        print('*', candidate_dict['Candidate_Name'], file=f, end='\n\n')
        print(" title:", candidate_dict['Office'], file=f, end='\n\n')
        # Didn't include label because as a mayor "City-Wide Office" is implied
        # and there is no good way to get the information from the data
