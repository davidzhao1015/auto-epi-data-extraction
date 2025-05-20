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
sys.path.append('/Users/xinzhao/ISMS_Work/Project_AIE/Working/python_codes/Epi_Toolbox_Py')  # Change the path to the folder containing the Epi_Toolbox_Py module

import importlib
import std_epi_parameters as std_epi # Import the standardization functions from the Epi_Toolbox_Py module
importlib.reload(std_epi) # Reload the module to ensure the latest version is used

# Todo (created on 2025.04.02):
# ✅ 1. Add format checks for input chat files using try-except
# 2. Handle slight variations in parameter names across chat files
# ✅ 3.1 Refactor custom functions for parsing study duration with better readability and maintainability
# 3.2 Optimize custom function for parsing study duration from free text "Literature review up to October 2021"
# ✅ 4.1 Refactor custom function to parse and standardize follow-up period
# 4.2 Improve function to extract IQR lower and upper bounds from follow-up period
# 5. Align parameter column names with those in the Data Hub
# 6. Write helper functions to safely apply custom functions to data frames
# 7. Refactor codes to implement reading text to data frames

# Solution to address 2 & 5: Link index of parameters with the Data Hub



#----------------------------------------------------------------

# List files in the folder

#----------------------------------------------------------------

# Change the working directory to the folder containing the txt files 
# os.chdir('/Users/xinzhao/ISMS_Work/Project_AIE/Working/chatgpt_outputs/chatgpt_output_epi/batch_testing')  # <-- Change the directory to the folder containing the txt files

from pathlib import Path

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

#--------------------------------------------------


# Extract Ref IDs from txt file names ...
# file_dict_epi_df = pd.DataFrame(list(file_dict_epi.items()), columns = ['File', 'Ref']) 
# file_dict_epi_df['Ref'] = file_dict_epi_df['Ref'].str.split("_").str[0]
# file_dict_epi_df.to_csv("file_dict_epi.csv", index=False)


#---------------------------------------------------------------

# Read Text Files into Data Frames

#---------------------------------------------------------------

chat_dict_epi = {} # Create a dictionary to store the chat output
for key0, value0 in file_dict_epi.items():
    # print(key0, value0)
    # Remove the line with "Quote(s)" in the txt file 
    with open(f"{value0}", "r") as f:
        lines = f.readlines()
        
        # Check if extra leading or trailing lines exist
        if len(lines) == 0 or 'article title' not in lines[0].lower():
            print(f"File {value0} might begin with extra leading lines.")
            continue
        if len(lines) == 0 or ':' not in lines[-1]:
            print(f"File {value0} might end with extra trailing lines.")
            continue
            
        lines = [line for line in lines if 'Line(s)' not in line]
        lines = [line for line in lines if 'Section' not in line] 
        lines = [line for line in lines if "Quote(s)" not in line]
        # Skip empty lines
        lines = [line for line in lines if line != '\n']
        lines = [line for line in lines if line != ""]
        lines = [line.strip("\t") for line in lines] 
        lines = [line.strip("[") for line in lines] # Remove the leading [
      
        chat_key = key0 # key is the index of the file
        chat_dict_epi[chat_key] = {} # Create a nested dictionary for each txt file 

        for line in lines:
            # print(line) # Check the content of the line
            if ":" in line and re.match(r'^\d+', line): 
                key1, value1 = line.split(":", 1)
                if value1 != '\n':
                    chat_dict_epi[chat_key][key1] = value1.strip() 

                if "Patient Number of Autoimmune Encephalitis" in key1:
                    ind = lines.index(line) + 1
                    try:
                        while not re.match(r"^\d+", lines[ind]): 
                            key2, value2 = lines[ind].split(":", 1) 
                            key2 = key1 + " " + key2.strip() + " " + str(ind) 
                            chat_dict_epi[chat_key][key2] = value2.strip()
                            ind += 1
                    except:
                        continue        

                if "Age of Patients" in key1:
                    ind = lines.index(line) + 1 
                    try:
                        while not re.match(r"^\d+", lines[ind]): 
                            key2, value2 = lines[ind].split(":", 1)
                            print(key2, f'the value is {value2}') # Check the key and value pairs

                            keywords = ['Mean', 'Median', 'SD', 'IQR', 'Subtype', 'Standard Deviation']
                            if all(keyword not in key2 for keyword in keywords): 
                                value3 = key2
                                key3 = key1 + " " + "Subtype" + " " + str(ind) # Add a unique identifier to the key
                                chat_dict_epi[chat_key][key3] = value3.strip()
                            else:
                                key3 = key1 + " " + key2.strip() + " " + str(ind) # Add a unique identifier to the key
                                chat_dict_epi[chat_key][key3] = value2.strip()
                                print(chat_dict_epi[chat_key])
                            ind += 1
                    except:
                        continue        

                if value1 == '\n':
                    print(f'key1: {key1}')
                    ind = lines.index(line) + 1
                    try:
                        while not re.match(r"^\d+", lines[ind]): 
                            key2, value2 = lines[ind].split(":", 1) 
                            key2 = key1 + " " + key2.strip() + str(ind)
                            chat_dict_epi[chat_key][key2] = value2.strip()
                            ind += 1
                    except:
                        continue
                else:
                    continue        

print(f'{len(chat_dict_epi)}/{len(file_dict_epi)} input files are parsed successfully.') 

# Todo: 
# Show input articles that are not parsed successfully


#---------------------------------------------------------------

# Convert the dictionary to a data frame

#--------------------------------------------------------------- 

chat_df = pd.DataFrame(columns = ["File", "Parameter", "Value"])
rows = []

for key3, value3 in chat_dict_epi.items():
    for parameter, cell in value3.items():
        rows.append({'File': key3, 'Parameter': parameter, 'Value': cell})

chat_df = pd.concat([chat_df, pd.DataFrame(rows)], ignore_index=True)   

chat_df.head()

# Export the data frame to a csv file
chat_df.to_csv("chat_df_epi.csv", index=False)


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
chat_df_5['Ref'] = chat_df_5['Ref'].str.split("_").str[0]

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