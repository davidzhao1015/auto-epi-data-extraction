#============================================================================
#
# This is a collection to custom functions that are commonly used to clean 
# and standardize epidemiological parameters
#
#============================================================================



#------------------------------------
# 
# Parse dates function
#
#------------------------------------

# step 1 - split study duration into start and end dates
def split_duration(duration):
    """
    Split the duration string into start and end years

    Parameters:
    duration: string
    
    Returns:
    start_year2: string
    end_year: string
    """
    import pandas as pd

    # Check if the input is NaN
    if pd.isna(duration):
        return '', ''
    
    # Check if it's a string and not empty
    if not isinstance(duration, str) or not duration.strip():
        return '', ''
    
    if duration == 'NR':
        return 'NR', 'NR'

    delimiters = ['to', '–', '-']
    for delimiter in delimiters:
        if delimiter in duration:
            parts = duration.split(delimiter)
            if len(parts) == 2:
                start_year = parts[0].strip()
                end_year = parts[1].strip()
                return start_year, end_year
    # Default fallback if no known delimiter found
    return '', ''

# # Test case:
# duration = '2010  - 2015'
# start_year2, end_year = split_duration(duration)
# print(f"Start Year: {start_year2}, End Year: {end_year}")

# print(split_duration(np.nan)) 


# step 2 - convert 'Month Year' or 'Year' to a full date string with assumed day
import calendar
from datetime import datetime

def parse_dates(input_string, is_start_year=True):
    """
    Convert 'Month Year' or 'Year' to a full date string with assumed day.
    - If is_start_year=True: returns the start of the period.
    - If is_start_year=False: returns the end of the period.
    - 'NR' is returned as-is.
    """
    if input_string == 'NR':
        return 'NR'

    parts = input_string.split()

    if len(parts) == 3:
        return input_string  # Full date provided

    if len(parts) == 1:
        # Only year provided
        return f"January 1, {parts[0]}" if is_start_year else f"December 31, {parts[0]}"

    if len(parts) == 2:
        # Month and year provided
        month, year_str = parts
        year = int(year_str)
        if is_start_year:
            return f"{month} 1, {year}"
        else:
            month_num = datetime.strptime(month, '%B').month
            last_day = calendar.monthrange(year, month_num)[1]
            return f"{month} {last_day}, {year}"

    raise ValueError(f"Invalid input format: '{input_string}'")

# # Test cases
# def test_parse_dates():
#     # Start dates
#     assert parse_dates("2020", is_start_year=True) == "January 1, 2020"
#     assert parse_dates("January 2020", is_start_year=True) == "January 1, 2020"
#     assert parse_dates("January 15, 2020", is_start_year=True) == "January 15, 2020"

#     # End dates
#     assert parse_dates("2020", is_start_year=False) == "December 31, 2020"
#     assert parse_dates("February 2020", is_start_year=False) == "February 29, 2020"  # Leap year
#     assert parse_dates("April 2021", is_start_year=False) == "April 30, 2021"
#     assert parse_dates("April 15, 2021", is_start_year=False) == "April 15, 2021"

#     # NR case
#     assert parse_dates("NR", is_start_year=True) == "NR"
#     assert parse_dates("NR", is_start_year=False) == "NR"

#     # Error case (invalid format)
#     try:
#         parse_dates("Invalid input", is_start_year=True)
#         assert False, "Expected ValueError for invalid input"
#     except ValueError:
#         pass  # Passed

#     print("All tests passed!")

# # Run the test
# test_parse_dates()



#------------------------------------
# 
# Parse Follow-up duration function
# 
#------------------------------------

import re

# step 1 - separate mean and median of follow-up period
def separate_mean_median(s):
    """
    Separate mean and median from the string.
    """
    if 'mean' in s.lower():
        return s, ''
    elif bool(re.search(r'\d', s)) and 'median' not in s.lower():
        return s, ''
    elif 'median' in s.lower():
        return '', s
    else:
        return '', ''  # No mean/median found
    

# # Test case
# s = 'mean 12.5 months'
# mean_part, median_part = separate_mean_median(s)
# print(f"Mean Part: {mean_part}, Median Part: {median_part}")
# s = 'median 10.5 months'
# mean_part, median_part = separate_mean_median(s)
# print(f"Mean Part: {mean_part}, Median Part: {median_part}")
# s = '12.5 months'
# mean_part, median_part = separate_mean_median(s)
# print(f"Mean Part: {mean_part}, Median Part: {median_part}")

# step 2 - extract digits and unit (year or month) from mean and median respectively
def find_time_with_units(s):
    """
    Extract digits and unit (year or month) from the string.
    """
    pattern = r'(\d+\.*\d*)\s*(month|months|year|years)'
    match = re.search(pattern, s)
    if match:
        return match.group(0)
    else:
        return s

# step 3 - convert year to month when the unit is year
def convert_year_to_month(s):
    """
    Convert year to month when the unit is year.
    """
    if 'year' in s:
        return str(int(float(s.split(' ')[0]) * 12)) + ' month'
    else:
        return s

# step 4 - remove "month" from the strings
def remove_month(s):
    """
    Remove "month" from the string.
    """
    return s.replace('month', '').strip()

# step 5 - convert the strings to float
def convert_to_float(s):
    """
    Convert the string to float.
    """
    try:
        return float(s)
    except ValueError:
        return s  # Return the original string if conversion fails

# Pipeline function to chain step 1-5
def process_follow_up_duration(s):
    """
    Process the follow-up duration string.
    """
    # Step 1: Separate mean and median
    mean_part, median_part = separate_mean_median(s)
    
    # Step 2: Extract digits and unit
    mean_part = find_time_with_units(mean_part)
    median_part = find_time_with_units(median_part)

    # Step 3: Convert year to month
    mean_part = convert_year_to_month(mean_part)
    median_part = convert_year_to_month(median_part)

    # Step 4: Remove "month"
    mean_part = remove_month(mean_part)
    median_part = remove_month(median_part)

    # Step 5: Convert to float
    mean_part = convert_to_float(mean_part)
    median_part = convert_to_float(median_part)

    return mean_part, median_part

# # Test case
# s = 'mean 12.5 months'
# mean_part, median_part = process_follow_up_duration(s)
# print(f"Mean Part: {mean_part}, Median Part: {median_part}")
# s = 'median 10.5 months'
# mean_part, median_part = process_follow_up_duration(s)
# print(f"Mean Part: {mean_part}, Median Part: {median_part}")
# s = '12.5 months'
# mean_part, median_part = process_follow_up_duration(s)
# print(f"Mean Part: {mean_part}, Median Part: {median_part}")
# s = 'mean 1.5 years'
# mean_part, median_part = process_follow_up_duration(s)
# print(f"Mean Part: {mean_part}, Median Part: {median_part}")


#---------------------------------------------------------------------------
#
# Standardize female % function
#
#----------------------------------------------------------------------------

def convert_string_to_float(s):
    """
    Convert a string to a float if it contains a percentage.
    """
    if '%' in s:
        return float(s.strip('%')) / 100
    else:
        return s
    

#--------------------------------------
#
# Standardize age group function
#
#--------------------------------------
def remove_string_in_parentheses(s):
    """
    Remove any string in parentheses from the input string.
    """
    return re.sub(r'\(.*\)', '', s)



#--------------------------------------
# 
# Map reported terms to HPO terms
#
#--------------------------------------
import requests

# Step 1 - Map reported symptoms to HPO terms using the HPA API
# Note: The HPA API is not always reliable. If the API fails, consider using a local database or a different API.
def map_symptoms_to_hpo(symptom):
    """
    Map reported symptoms to HPO terms using the HPA API.
    """
    url = f"https://ontology.jax.org/api/hp/search/?q={symptom}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises HTTPError if not 200 OK
        json_data = response.json()
        results = json_data.get('terms', [])
        if results:
            top = results[0]  # Take top result
            return (top["name"], top["id"])  # return matched term and HPO ID as a tuple
        else:
            return (None, None)
    except requests.exceptions.RequestException as e:
        # print(f"Request failed for term '{symptom}': {e}")
        return (None, None)
    except ValueError as ve:
        # print(f"Invalid JSON for term '{symptom}': {ve}")
        return (None, None)


#-------------------------------------------------------------------------------------------------
# Algorithm to verify HPO terms
# 1. Calculate the fuzzy or cosine similarity score between the input term and the matched term
# 2. If the score is above a certain threshold (e.g., 0.8), consider it a match.
# 3. If the score is below the threshold, check if the matched term is a synonym of the input term.
# 4. If it is, consider it a match.
# 5. If not, return None or a message indicating no match was found.
#-------------------------------------------------------------------------------------------------

from fuzzywuzzy import process
import pandas as pd

# Step 2 - Standardize clinical terms using cosine similarity, fuzzy matching, and semantic similarity
# Note: This function requires the `spacy` library and the `en_core_web_md` model.
def estimate_fuzzy_score(input_term, hpo_term):
    """
    Estimate the fuzzy score between the input term and the HPO term.

    Parameters:
    input_term: str
        The term reported in the study.
    hpo_term: str
        The term from the HPO database.
    Returns:
    fuzzy_score: float
        The fuzzy score between the input term and the HPO term.

    """
    if not isinstance(input_term, str):
        raise ValueError("reported_term must be a string.")
    
    best_match_fuzzy, fuzzy_score = process.extractOne(input_term, [hpo_term])
    return fuzzy_score

# # Test case 
# input_term = "fever"
# hpo_term = "Fever"
# fuzzy_score = estimate_fuzzy_score(input_term, hpo_term)
# print(f"Fuzzy Score: {fuzzy_score}")


# Step 3 - Look up HPO synonyms and definition
import obonet
def get_hpo_definitions_and_synonyms(hpo_id):
    """
    Get the definition and synonyms for a given HPO term ID.
    """
    url = 'http://purl.obolibrary.org/obo/hp.obo' # URL points to the Human Phenotype Ontology (HPO) in OBO format, hosted by the OBO Foundry
    graph = obonet.read_obo(url)

    if hpo_id in graph.nodes:
        synonyms = graph.nodes[hpo_id].get('synonyms', [])
        definition = graph.nodes[hpo_id].get('def', 'NA')
        return synonyms, definition
    else:
        return None, None
    
# Pipeline function to chain step 1-3
def map_symptoms_to_hpo_pipeline(symptom):
    """
    Map reported symptoms to HPO terms and get synonyms and definitions.

    Parameters:
    symptom: str
        The term reported in the study.
    Returns:
    hpo_term: str
        The term from the HPO database.
    hpo_id: str
        The ID of the term from the HPO database.
    fuzzy_score: float
        The fuzzy score between the input term and the HPO term.
    status: str
        The status of the mapping ('matched' or 'not matched').
    """
    # Step 1: Map reported symptoms to HPO terms
    hpo_term, hpo_id = map_symptoms_to_hpo(symptom)
    
    # Step 2: Estimate fuzzy score
    fuzzy_score = estimate_fuzzy_score(symptom, hpo_term)

    # Step 3: Get HPO definitions and synonyms
    synonyms, definition = get_hpo_definitions_and_synonyms(hpo_id)

    if fuzzy_score >= 80 or hpo_term.lower() in synonyms:
        return hpo_term, hpo_id, fuzzy_score, 'matched'
    else:
        return hpo_term, hpo_id, fuzzy_score, 'not matched'
    
# # Test case 
# symptom = "fever"
# hpo_term, hpo_id, fuzzy_score, status = map_symptoms_to_hpo_pipeline(symptom)
# print(f"HPO Term: {hpo_term}, HPO ID: {hpo_id}, Fuzzy Score: {fuzzy_score}, Status: {status}")    