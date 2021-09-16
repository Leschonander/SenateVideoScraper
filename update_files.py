import pandas as pd
import os
import time
from datetime import datetime

budget = pd.read_csv("./SenateVideoFiles/Budget.csv")
energy = pd.read_csv("./SenateVideoFiles/Energy.csv")
JEC = pd.read_csv("./SenateVideoFiles/JEC.csv")
IndianAffairs = pd.read_csv("./SenateVideoFiles/IndianAffairs.csv")

def date_convert_dots(date):
    try:
        return datetime.strptime(date, '%m.%d.%y ').strftime("%m/%d/%Y")
    except:
        return date

def date_convert_name(date):
    try:
        return datetime.strptime(date, '%b %d %Y').strftime("%m/%d/%Y")
    except:
        return date

def date_convert_name_indian(date):

    try:
        return datetime.strptime(date, '%b %d, %Y').strftime("%m/%d/%Y")
    except:
        return date

budget['Date'] = budget['Date'].apply(date_convert_dots)
energy['Date'] = energy['Date'].apply(date_convert_name)
JEC['Date'] = JEC['Date'].apply(date_convert_name)
IndianAffairs['Date'] = IndianAffairs['Date'].apply(date_convert_name_indian)

budget = budget.to_csv("./SenateVideoFiles/Budget.csv")
energy = energy.to_csv("./SenateVideoFiles/Energy.csv")
JEC = JEC.to_csv("./SenateVideoFiles/JEC.csv")
IndianAffairs = IndianAffairs.to_csv("./SenateVideoFiles/IndianAffairs.csv")