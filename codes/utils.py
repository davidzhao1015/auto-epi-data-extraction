#-----------------------------------------------------------
# Load libraries
#-----------------------------------------------------------

import pandas as pd
import numpy as np
import os

from sklearn.feature_extraction.text import TfidfVectorizer # Term Frequency-Inverse Document Frequency (TF-IDF)
from sklearn.feature_extraction.text import CountVectorizer # CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity # Cosine similarity

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import logging



#-----------------------------------------------------------
# Load reported terms and standard terms
#-----------------------------------------------------------

def load_reported_terms(file_path, sheet_name, header_row, col_name):
    if file_path.endswith('.xlsb'):
        df = pd.read_excel(file_path, 
                           sheet_name=sheet_name, 
                           header=header_row, 
                           engine='pyxlsb',
                           na_values=[], keep_default_na=False) # Prevent "NA" from being read as NaN
    else:
        df = pd.read_excel(file_path, 
                           sheet_name=sheet_name, 
                           header=header_row,
                           na_values=[], keep_default_na=False) # Prevent "NA" from being read as NaN
    reported_terms = df[col_name]
    return reported_terms

def load_std_terms(file_path, sheet_name, header_row, col_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    std_terms = df[col_name].to_list()
    std_terms = [term for term in std_terms if isinstance(term, str) and term.strip()]  # Keep only non-empty strings
    std_terms = list(set(std_terms))  # Remove duplicates
    return std_terms

def save_results_to_excel(results, file_path):
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        results.to_excel(writer, index=False)    