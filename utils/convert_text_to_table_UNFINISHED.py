#===========================================================================================
# This script is used to tabularize the chat output of the epi data for eco burden articles
#===========================================================================================

import re
import pandas as pd
import numpy as np
import os

import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


import sys
# sys.path.append('/Users/xinzhao/ISMS_Work/Project_AIE/Working/python_codes/Epi_Toolbox_Py')  # Change the path to the folder containing the Epi_Toolbox_Py module

# import importlib
# import std_epi_parameters as std_epi # Import the standardization functions from the Epi_Toolbox_Py module
# importlib.reload(std_epi) # Reload the module to ensure the latest version is used
from pathlib import Path


#----------------------------------------------------------------

# List files in the folder

#----------------------------------------------------------------

def get_file_list(directory, file_extension):
    """
    List all files in the directory with the specified file extension.
    
    Args:
        dict: The absolute path to a dictionary of files with the specified extension.
        file_extension (str): The file extension to filter by.
        
    Returns:
        dict: A dictionary of files with the specified extension.
    """

    directory = Path(directory)
    if not directory.is_dir():
        logging.error(f"The specified path {directory} is not a directory.")
        return {}
    if not directory.exists():
        logging.error(f"The specified path {directory} does not exist.")
        return {}
    
    # Get the list of files in the directory with the specified extension
    file_list = [file for file in directory.glob(f"*.{file_extension}") if file.is_file()]
    
    file_list.sort()
    print(f"Sorted file list: {file_list}")
    logging.info(f"Number of files with {file_extension} extension: {len(file_list)}")

    # Check if the file list is empty
    if not file_list:
        logging.warning("No files found with the specified extension.")
        return {}

    # Convert the list to a dictionary 
    file_dict_epi = {i:file_list[i] for i in range(0, len(file_list))} 
    logging.info(f"The resulting dictionary contains {len(file_dict_epi)} files.")
    
    return file_dict_epi



# Test case
input_files = get_file_list("example_input/chatgpt_output_batch_testing", 'txt')
print(input_files)




#--------------------------------------------------


def get_ref_id_from_filename(file_dict_epi):
    """
    Extract the reference ID from the filenames in the dictionary.

    Args:
        file_dict_epi (dict): A dictionary of files with the specified extension.

    Returns:
        pd.DataFrame: A DataFrame containing the reference ID and the corresponding file name.
    """
    ref_id_df = pd.DataFrame(
        [(key, str(value)) for key, value in file_dict_epi.items()], 
        columns=['File', 'Ref']
    )
    ref_id_df['Ref'] = ref_id_df['Ref'].apply(
        lambda x:  re.search(r'\d+(?=\D+\.txt)', x).group() if re.search(r'\d+(?=\D+\.txt)', x) else "unknown_ref"
    )
    return ref_id_df

# Test case
print(input_files)

ref_id_df = get_ref_id_from_filename(input_files)
print(ref_id_df)


#---------------------------------------------------------------

# Read Text Files into Data Frames

#---------------------------------------------------------------


# def parse_text_file(file_dict_epi):
#     """
#     Parses .txt files and extracts key-value pairs from structured text.
    
#     Args:
#         file_dict_epi (dict): Dictionary with keys as indices and values as filenames (not full paths).
    
#     Returns:
#         dict: Nested dictionary with parsed key-value pairs.
#     """
#     chat_dict_epi = {} # Create a dictionary to store the chat output
    
#     for key0, value0 in file_dict_epi.items():
#         # print(key0, value0)
#         # Remove the line with "Quote(s)" in the txt file 
#         with open(f"{value0}", "r") as f:
#             lines = f.readlines()
            
#             # Check if extra leading or trailing lines exist
#             if len(lines) == 0 or 'article title' not in lines[0].lower():
#                 print(f"File {value0} might begin with extra leading lines.")
#                 continue
#             if len(lines) == 0 or ':' not in lines[-1]:
#                 print(f"File {value0} might end with extra trailing lines.")
#                 continue
                
#             lines = [line for line in lines if 'Line(s)' not in line]
#             lines = [line for line in lines if 'Section' not in line] 
#             lines = [line for line in lines if "Quote(s)" not in line]
#             # Skip empty lines
#             lines = [line for line in lines if line != '\n']
#             lines = [line for line in lines if line != ""]
#             lines = [line.strip("\t") for line in lines] 
#             lines = [line.strip("[") for line in lines] # Remove the leading [
        
#             chat_key = key0 # key is the index of the file
#             chat_dict_epi[chat_key] = {} # Create a nested dictionary for each txt file 

#             for line in lines:
#                 # print(line) # Check the content of the line
#                 if ":" in line and re.match(r'^\d+', line): 
#                     key1, value1 = line.split(":", 1)
#                     if value1 != '\n':
#                         chat_dict_epi[chat_key][key1] = value1.strip() 

#                     if "Patient Number of Autoimmune Encephalitis" in key1:
#                         ind = lines.index(line) + 1
#                         try:
#                             while not re.match(r"^\d+", lines[ind]): 
#                                 key2, value2 = lines[ind].split(":", 1) 
#                                 key2 = key1 + " " + key2.strip() + " " + str(ind) 
#                                 chat_dict_epi[chat_key][key2] = value2.strip()
#                                 ind += 1
#                         except:
#                             continue        

#                     if "Age of Patients" in key1:
#                         ind = lines.index(line) + 1 
#                         try:
#                             while not re.match(r"^\d+", lines[ind]): 
#                                 key2, value2 = lines[ind].split(":", 1)
#                                 print(key2, f'the value is {value2}') # Check the key and value pairs

#                                 keywords = ['Mean', 'Median', 'SD', 'IQR', 'Subtype', 'Standard Deviation']
#                                 if all(keyword not in key2 for keyword in keywords): 
#                                     value3 = key2
#                                     key3 = key1 + " " + "Subtype" + " " + str(ind) # Add a unique identifier to the key
#                                     chat_dict_epi[chat_key][key3] = value3.strip()
#                                 else:
#                                     key3 = key1 + " " + key2.strip() + " " + str(ind) # Add a unique identifier to the key
#                                     chat_dict_epi[chat_key][key3] = value2.strip()
#                                     print(chat_dict_epi[chat_key])
#                                 ind += 1
#                         except:
#                             continue        

#                     if value1 == '\n':
#                         print(f'key1: {key1}')
#                         ind = lines.index(line) + 1
#                         try:
#                             while not re.match(r"^\d+", lines[ind]): 
#                                 key2, value2 = lines[ind].split(":", 1) 
#                                 key2 = key1 + " " + key2.strip() + str(ind)
#                                 chat_dict_epi[chat_key][key2] = value2.strip()
#                                 ind += 1
#                         except:
#                             continue
#                     else:
#                         continue
                
#         print(f'{len(chat_dict_epi)}/{len(file_dict_epi)} input files are parsed successfully.')

import re
import logging
from pathlib import Path

def parse_text_file(file_dict_epi, target_disease_name):
    """
    Parses .txt files and extracts key-value pairs from structured text.
    
    Args:
        file_dict_epi (dict): Dictionary with keys as indices and values as filenames (not full paths).
        target_disease_name (str): The name of the target disease to filter the data by.
    
    Returns:
        dict: Nested dictionary with parsed key-value pairs.
    """
    chat_dict_epi = {}

    def clean_lines(lines):
        """Remove unwanted lines and characters."""
        return [
            line.strip().strip("[") for line in lines
            if line.strip() and
               all(skip not in line for skip in ['Line(s)', 'Section', 'Quote(s)'])
        ]

    def extract_additional_lines(start_index, lines, key_prefix):
        """Extract key-value pairs from follow-up lines after a multi-line key."""
        extracted = {}
        index = start_index
        try:
            while index < len(lines) and not re.match(r"^\d+", lines[index]):
                if ':' in lines[index]:
                    subkey, subval = lines[index].split(':', 1)
                    full_key = f"{key_prefix} {subkey.strip()} {index}"
                    extracted[full_key] = subval.strip()
                index += 1
        except Exception as e:
            logging.warning(f"Error extracting additional lines after line {start_index}: {e}")
        return extracted

    for key, filename in file_dict_epi.items():
        try:
            with open(filename, "r") as f:
                lines = f.readlines()

            if not lines or 'article title' not in lines[0].lower():
                logging.warning(f"File {filename} might have extra leading lines. Skipping.")
                continue
            if not lines[-1] or ':' not in lines[-1]:
                logging.warning(f"File {filename} might have extra trailing lines. Skipping.")
                continue

            lines = clean_lines(lines)
            chat_dict_epi[key] = {}

            for i, line in enumerate(lines):
                if ':' in line and re.match(r'^\d+', line):
                    key1, value1 = line.split(":", 1)
                    key1 = key1.strip()
                    value1 = value1.strip()
                    chat_dict_epi[key][key1] = value1

                    if f"Patient Number of {target_disease_name}" in key1:
                        chat_dict_epi[key].update(
                            extract_additional_lines(i + 1, lines, key1)
                        )

                    elif "Age of Patients" in key1:
                        index = i + 1
                        try:
                            while index < len(lines) and not re.match(r"^\d+", lines[index]):
                                if ':' in lines[index]:
                                    k2, v2 = lines[index].split(":", 1)
                                    k2 = k2.strip()
                                    v2 = v2.strip()
                                    if all(kw not in k2 for kw in ['Mean', 'Median', 'SD', 'IQR', 'Subtype', 'Standard Deviation']):
                                        full_key = f"{key1} Subtype {index}"
                                        chat_dict_epi[key][full_key] = k2
                                    else:
                                        full_key = f"{key1} {k2} {index}"
                                        chat_dict_epi[key][full_key] = v2
                                index += 1
                        except Exception as e:
                            logging.warning(f"Error processing 'Age of Patients' block in {filename}: {e}")

                    elif not value1:  # Empty value; continue extraction
                        chat_dict_epi[key].update(
                            extract_additional_lines(i + 1, lines, key1)
                        )

        except Exception as e:
            logging.error(f"Failed to process file {filename}: {e}")
            continue

    logging.info(f"{len(chat_dict_epi)}/{len(file_dict_epi)} input files parsed successfully.")
    # Detect any files not processed successfully
    if len(chat_dict_epi) != len(file_dict_epi):
        logging.info(f"The files failed to process including {[value.name for key, value in file_dict_epi.items() if key not in chat_dict_epi.keys()]}")
    return chat_dict_epi

# Test case
parsed_text_files = parse_text_file(input_files, "Autoimmune Encephalitis")


#---------------------------------------------------------------

# Convert the dictionary to a data frame

#--------------------------------------------------------------- 


def convert_dict_to_df(parsed_text_files):
    """
    Convert a nested dictionary (parsed from text files) into a flat DataFrame.

    Args:
        parsed_text_files (dict): Dictionary of dictionaries with file names as keys and parameter-value pairs as values.

    Returns:
        pd.DataFrame: A DataFrame with columns ['File', 'Parameter', 'Value'].
    """
    rows = [
        {'File': file_key, 'Parameter': param, 'Value': val}
        for file_key, params in parsed_text_files.items()
        for param, val in params.items()
    ]

    return pd.DataFrame(rows)

# Test case
chat_df_epi = convert_dict_to_df(parsed_text_files)
print(chat_df_epi.head(20))



#---------------------------------------------------------------

# Drop subtype-specific parameters for separate processing *

#---------------------------------------------------------------
# Drop rows with "22.    Age of Patients by Subtype"
chat_df_dropped = chat_df[~chat_df['Parameter'].str.contains('Age of Patients')]

# Drop rows with "Patient Number of Autoimmune Encephalitis"
chat_df_dropped2 = chat_df_dropped[~chat_df_dropped['Parameter'].str.contains('Patient Number of Autoimmune Encephalitis')]

# Drop rows with "Age of Diagnosis"
chat_df_dropped2 = chat_df_dropped2[~chat_df_dropped2['Parameter'].str.contains('Age of Diagnosis')]

# Export the data frame to a csv file
chat_df_dropped2.to_csv("chat_df_epi_2.csv", index=False)



#---------------------------------------------------------------

# Clean parameter names, remove special characters

#---------------------------------------------------------------

# Remove digits and periods from the parameter names
chat_df_3 = chat_df_dropped2.copy()
chat_df_3['Parameter'] = chat_df_dropped2['Parameter'].str.replace(r'^\d+(\.|\])*\s*', '', regex=True)

# Trim white spaces from the parameter names
chat_df_3['Parameter'] = chat_df_3['Parameter'].str.strip()

# Turn the parameter names into small cases
chat_df_3['Parameter'] = chat_df_3['Parameter'].str.lower()


# Export the data frame to a csv file
chat_df_3.to_csv("chat_df_epi_3.csv", index=False)


#---------------------------------------------------------------

# Reshape the data frame

#---------------------------------------------------------------

# Make long table wide
chat_df_4 = chat_df_3.pivot(index='File', columns='Parameter', values='Value').reset_index() 

chat_df_4.to_csv("chat_df_epi_4.csv", index=False)




#---------------------------------------------------------------

# Map Ref to the data frame

#---------------------------------------------------------------
# Add the reference to the data frame
chat_df_5 = chat_df_4.copy()
chat_df_5['Ref'] = chat_df_5['File'].map(file_dict_epi)
chat_df_5['Ref'] = chat_df_5['Ref'].apply(
    lambda x: x.split("_")[0] if "_" in x else "Unknown_Ref"
)

chat_df_5.to_csv("chat_df_epi_5.csv", index=False)




# #---------------------------------------------------------------

# # Standardize certain parameters - Study duration

# #---------------------------------------------------------------

# # Split the study duration into start and end years
# split_duration_df = chat_df_5.copy() # Create a copy of the data frame
# split_duration_df[['Source start year', 'Source end year']] = split_duration_df['study duration'].apply(std_epi.split_duration).apply(pd.Series)


# # Clean the "Source start year" and "Source end year" columns 
# chat_df_7 = split_duration_df.copy() # Create a copy of the data frame 
# chat_df_8 = chat_df_7.copy()

# chat_df_8['Source start year'] = chat_df_7['Source start year'].apply(std_epi.parse_dates, if_start_year=True) 
# chat_df_8['Source end year'] = chat_df_7['Source end year'].apply(std_epi.parse_dates, if_start_year=False) 

# chat_df_9 = chat_df_8.copy()

# chat_df_9['Source start year'] = pd.to_datetime(chat_df_8['Source start year'], errors='coerce') # Convert the columns to datetime objects 
# chat_df_9['Source end year'] = pd.to_datetime(chat_df_8['Source end year'], errors='coerce')  # Convert the columns to datetime objects 

# chat_df_9.to_csv("chat_df_epi_7.csv", index=False)


# #---------------------------------------------------------------

# # Standardize follow-up period

# #---------------------------------------------------------------

# # Add the follow-up periods to the data frame
# chat_df_10 = chat_df_9.copy()

# if 'follow-up period' in chat_df_9.columns:
#     chat_df_10[['Follow-up period mean', 'Follow-up period median']] = (
#         chat_df_9['follow-up period']
#         .apply(std_epi.process_follow_up_duration)
#         .apply(pd.Series)
#     )
# else:
#     print("Column 'follow-up period' is missing. Skipping this step.")

# chat_df_10.to_csv("chat_df_epi_8.csv", index=False)



# #---------------------------------------------------------------

# # Standardize female percentage in cohort

# #---------------------------------------------------------------
    
# chat_df_11 = chat_df_10.copy()
# chat_df_11['female percentage in cohort'] = chat_df_10['female percentage in cohort'].apply(std_epi.convert_string_to_float)  

# chat_df_11.to_csv("chat_df_epi_9.csv", index=False)


# #---------------------------------------------------------------

# # Standardize cohort age group

# #---------------------------------------------------------------

# chat_df_12 = chat_df_11.copy()

# # Check if the column 'cohort age group' exists before applying the function
# if 'cohort age group' in chat_df_11.columns:
#     chat_df_12['cohort age group'] = chat_df_11['cohort age group'].apply(std_epi.standardize_age_group)
# else:
#     print("Column 'cohort age group' is missing. Skipping this step.")

# chat_df_12.to_csv("chat_df_epi_10.csv", index=False)