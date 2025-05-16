#=============================================================================================
# This script processes the outputs from chat-based extraction related to
# epidemiological (epi) data and economic burden (eco burden) data.
# Specifically, it parses and extracts patient numbers associated with
# different subtypes of autoimmune encephalitis from the chat outputs.
#=============================================================================================

import os
import re 
import sys
import pandas as pd
import numpy as np
import pyxlsb
import argparse
import logging


#--------------------------------------------------------------------------------------------
# Step 1: Load the chat outputs
#--------------------------------------------------------------------------------------------

def load_chat_epi_data(file_path):
    """
    Load the chat outputs from a CSV file.
    """
    return pd.read_csv(file_path)


def set_working_directory(file_path):
    """
    Set the working directory.
    """
    folder_path = os.path.dirname(file_path)
    os.chdir(folder_path)
    print(f"Working directory set to: {folder_path}")


# # Test the function
# file_path = "/Users/xinzhao/ISMS_Work/Project_AIE/Working/chatgpt_outputs/chatgpt_output_epi/batch_4_eco/chat_df_epi.csv"

# set_working_directory(file_path)
# chat_epi = load_chat_epi_data(file_path)
# print(chat_epi.head(20))


def get_valid_file_path(prompt_msg):
    while True:
        path = input(prompt_msg).strip()
        if not path:
            print("Error: File path cannot be empty. Please try again.")
            continue
        if not os.path.isfile(path):
            print(f"Error: The file '{path}' does not exist.")
            continue
        return path

def get_output_file_name():
    filename = input("Enter the output file name (default: output_epi_patient_number.csv): ").strip() or "output_epi_patient_number.csv"
    return filename


#-------------------------------------------------------------------------------------------
# Step 2: Subset Total AIE
#-------------------------------------------------------------------------------------------

def subset_subtype_patient_number(df, parameter, regex_pattern, column = "Parameter", save_to_csv=False):
    """
    Subset rows with the target parameter and clean the parameter column.

    Args:
        df (pd.DataFrame): The input DataFrame containing chat outputs.
        parameter (str): The target parameter to subset (e.g., "Patient Number of Autoimmune Encephalitis").
        regex_pattern (str): The regex pattern to clean the parameter column.
        column (str): The column to subset (default is 'Parameter').
        save_to_csv (bool): Whether to save the subsetted DataFrame to a CSV file (default is False).

    Returns:
        pd.DataFrame: A DataFrame containing the subsetted and cleaned data.
    """
    df_subset = df[df[column].str.contains(parameter, na=False)] # Subset rows with target parameter (e.g "Patient Number of Autoimmune Encephalitis")

    df_subset2 = df_subset.copy()

    try:
        re.compile(regex_pattern)  # Validate the regex pattern
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {regex_pattern}. Error: {e}")

    df_subset2[column] = (df_subset[column]
                                     .str.replace(regex_pattern, "", regex = True)) # regex_pattern represents the item in ChatGPT output (eg. 20. Patient Number of Autoimmune Encephalitis)
    
    df_subset2[column] = df_subset2[column].apply(lambda x: "cohort_patient" if x == "" else x)

    if save_to_csv:
        df_subset2.to_csv('output_step_1.csv', index=False)

    return df_subset2



# # Test case 
# chat_epi_subset = subset_subtype_patient_number(chat_epi, 
#                                                 "Patient Number of Autoimmune Encephalitis", 
#                                                 r'20\.\s*Patient Number of Autoimmune Encephalitis')

# print(chat_epi_subset.head(20))


#-------------------------------------------------------------------------------------------
# Step 3: Clean the chat_epi_subset
#-------------------------------------------------------------------------------------------

def clean_chat_epi_subset(df):
    """
    Clean the chat_epi_subset DataFrame by removing empty rows and resetting the index.

    Args:
        df (pd.DataFrame): The input DataFrame containing chat outputs.

    Returns:
        pd.DataFrame: A cleaned DataFrame with empty rows removed and index reset.
    """
    df2 = df[df['Parameter'].notna() & (df['Parameter'] != "")]
    if 'Value' in df2.columns:
        df2 = df2[df2['Value'].notnull()]
    else:
        raise KeyError("The 'Value' column is missing in the DataFrame.")
    df2 = df2.reset_index(drop=True)  # Reset index
    df2['Parameter'] = df2['Parameter'].str.replace(r'•\t', "", regex=True).str.strip()
    df2['Value'] = df2['Value'].str.strip()
    return df2

# # Test case
# chat_epi_subset5 = clean_chat_epi_subset(chat_epi_subset)
# print(chat_epi_subset5.head())
    

#-------------------------------------------------------------------------------------------
# Step 4: Pair subtype with patient number
#-------------------------------------------------------------------------------------------

def pair_subtype_patient_number(df):
    """
    Pair subtype with patient number and create a new DataFrame.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing chat outputs.
        
    Returns:
        pd.DataFrame: A DataFrame containing the paired subtype and patient number.
    """
    subtype_number_pair = []
    for i in range(len(df)):
        if 'Subtype' in df.loc[i, 'Parameter']:
            subtype = df.loc[i, 'Value']
            patient_number = df.loc[i + 1, 'Value'] if (i+1 <= len(df) and 'Value' in df.columns)  else None
            if 'File' in df.columns:
                ref = df.loc[i, 'File']
            else:
                raise KeyError("The 'File' column is missing in the DataFrame.")
            ref = str(ref)
            subtype_number_pair.append([ref, subtype, patient_number])

    # Concatenate the list of lists into a dataframe
    subtype_number_df = pd.DataFrame(subtype_number_pair, columns = ['File', 'Parameter', 'Value'])

    # Drop rows with Parameter != Total AIE
    df2 = df[df['Parameter'].str.contains("cohort_patient")]

    df2 = df2.reset_index(drop=True)
    subtype_number_df = subtype_number_df.reset_index(drop=True)
    df3 = pd.concat([df2, subtype_number_df], axis=0).reset_index(drop=True)

    return df3
    

# # Test case
# chat_epi_subset5_2 = pair_subtype_patient_number(chat_epi_subset5)
# print(chat_epi_subset5_2.head(20))


 

#-------------------------------------------------------------------------------------------
# Step 5: Standardize Value column
#-------------------------------------------------------------------------------------------

def standardize_numeric_column(df, column):
    """
    Standardize a numeric column by removing non-digits, commas, and converting to numeric.

    Args:
        df (pd.DataFrame): The input DataFrame containing chat outputs.
        column (str): The column to standardize.

    Returns:
        pd.DataFrame: A DataFrame with the standardized numeric column.
    """
    df2 = df.copy()
    df2[column] = df[column].str.replace(r'\D', "", regex=True) # Remove non-digits
    df2[column] = df2[column].str.replace(r',', "", regex=True) # Remove comma
    df2[column] = df2[column].str.strip() # Strip whitespace
    df2[column] = pd.to_numeric(df2[column], errors='coerce') # Convert to numeric
    return df2

# # Test case
# chat_epi_subset6 = standardize_numeric_column(chat_epi_subset5_2, 'Value')
# print(chat_epi_subset6.head(20))


#-------------------------------------------------------------------------------------------
# Step 6: Add Ref column
#-------------------------------------------------------------------------------------------


def map_ref_to_study(df, ref_file, study_col='File'):
    """
    Map the file column to the reference file and return a new DataFrame.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing chat outputs.
        ref_file (str): The path to the reference file.
        study_col (str): The column name to be converted to integer (default is 'File').
        
    Returns:
        pd.DataFrame: A DataFrame with the study column mapped to the reference file.
    """
    df2 = df.copy()
    df2[study_col] = df2[study_col].astype(int)

    ref_df = pd.read_csv(ref_file)

    df_merged = pd.merge(df2, ref_df, on=study_col, how='left')
    df_merged2 = df_merged.drop(columns=[study_col])

    return df_merged2

# # Test case
# ref_file = "/Users/xinzhao/ISMS_Work/Project_AIE/Working/chatgpt_outputs/chatgpt_output_epi/batch_4_eco/file_dict_epi.csv"
# chat_epi_subset9 = map_ref_to_study(chat_epi_subset6, study_col='File', ref_file=ref_file)
# print(chat_epi_subset9.head(20))



#--------------------------------------------------------------------------------------------
# Step 7: Map cohort_patient to study patient number
#--------------------------------------------------------------------------------------------

def map_cohort_patient(df):
    total_aie_dict = dict(zip(df[df['Parameter'] == "cohort_patient"]['Ref'],
                          df[df['Parameter'] == "cohort_patient"]['Value']))

    # Create a column "Denominator" for the total number of AIE patients in each study
    df2 = df.copy()
    df2['Study patient number'] = df['Ref'].map(total_aie_dict)

    # Convert Value and Denominator to numeric
    df2['Value'] = pd.to_numeric(df2['Value']) 
    df2['Study patient number'] = pd.to_numeric(df2['Study patient number']) 

    # Drop rows with Parameter = Total AIE
    df3 = df2[df2['Parameter'] != "cohort_patient"]

    new_columns = {"Parameter": "Subtype", 
                   "Value": "Subtype patient number"
                   }
    
    df3 = df3.rename(columns = new_columns)

    df3 = df3[['Ref', 'Subtype', 'Subtype patient number', 'Study patient number']]
    df3 = df3.reset_index(drop=True)

    return df3
        
# # Test case
# chat_epi_subset11 = map_cohort_patient(chat_epi_subset9)
# print(chat_epi_subset11.head(30))  



#--------------------------------------------------------------------------------------------
#
# Main function to run the entire process
# 
#--------------------------------------------------------------------------------------------

def main():
    """
    Main function to run the entire process.
    """
    # Set up logging configuration
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler('process.log')])
    
    logging.info("Starting the process...")

    # Get the file path and output file name
    file_path = get_valid_file_path("Enter the absolute path to the input CSV file: ")
    output_file = get_output_file_name()
    logging.info(f"Output file name: {output_file}")
    
    # Get the regex pattern for the target parameter
    print("Enter the regex pattern for the target parameter.")
    print("Example: '20\\.\\s*Patient Number of Autoimmune Encephalitis' matches '20. Patient Number of Autoimmune Encephalitis'.")
    regex_pattern = input("Regex pattern (press Enter to use the default): ").strip()
    if not regex_pattern:
        regex_pattern = r'20\.\s*Patient Number of Autoimmune Encephalitis'
        # print(f"No regex entered. Using default pattern: {regex_pattern}")
        logging.info(f"No regex entered. Using default pattern: {regex_pattern}")

    # Get the reference file path
    ref_file = input("Enter the absolute path to the reference file (default: /Users/xinzhao/ISMS_Work/Project_AIE/Working/chatgpt_outputs/chatgpt_output_epi/batch_4_eco/file_dict_epi.csv): ").strip() or "/Users/xinzhao/ISMS_Work/Project_AIE/Working/chatgpt_outputs/chatgpt_output_epi/batch_4_eco/file_dict_epi.csv"
    if not os.path.isfile(ref_file):
        # print(f"Error: The reference file '{ref_file}' does not exist. Please check the path and try again.")
        logging.error(f"Error: The reference file '{ref_file}' does not exist. Please check the path and try again.")
        sys.exit(1)

    # Set the working directory
    set_working_directory(file_path)

    # Load the chat outputs
    chat_epi = load_chat_epi_data(file_path)
    # print(f"Loaded {len(chat_epi)} rows from the input file.")
    logging.info(f"Loaded {len(chat_epi)} rows from the input file.")

    # Subset Total AIE
    chat_epi_subset = subset_subtype_patient_number(chat_epi, 
                                                    "Patient Number of Autoimmune Encephalitis", 
                                                    regex_pattern=regex_pattern)
    
    # Validate if the regex pattern matches any rows
    if chat_epi_subset.empty:
        # print(f"Error: The regex pattern '{regex_pattern}' did not match any rows in the input data.")
        logging.error(f"Error: The regex pattern '{regex_pattern}' did not match any rows in the input data.")
        sys.exit(1)

    # Clean the chat_epi_subset
    chat_epi_subset5 = clean_chat_epi_subset(chat_epi_subset)

    # Pair subtype with patient number
    chat_epi_subset5_2 = pair_subtype_patient_number(chat_epi_subset5)

    # Standardize Value column
    chat_epi_subset6 = standardize_numeric_column(chat_epi_subset5_2, 'Value')

    # Add Ref column
    chat_epi_subset9 = map_ref_to_study(chat_epi_subset6, study_col='File', ref_file=ref_file)

    # Map cohort_patient to study patient number
    chat_epi_subset11 = map_cohort_patient(chat_epi_subset9)
    
    logging.info(f"The preview of the resulting table is \n{chat_epi_subset11.head()}")
    
    # Save the final DataFrame to a CSV file
    chat_epi_subset11.to_csv(os.path.abspath(output_file), index=False)
    try:
        # print(f"Final DataFrame saved to: {os.path.abspath(output_file)}")
        logging.info(f"Final DataFrame saved to: {os.path.abspath(output_file)}")
    except PermissionError:
        # print(f"Error: Permission denied. Unable to save the file to {output_file}. Please check your permissions.")
        logging.error(f"Error: Permission denied. Unable to save the file to {output_file}. Please check your permissions.")
    except FileNotFoundError:
        print(f"Error: The directory for the file '{output_file}' does not exist. Please check the file path.")
        logging.error(f"Error: The directory for the file '{output_file}' does not exist. Please check the file path.")
    except Exception as e:
        # print(f"An unexpected error occurred while saving the file: {e}")
        logging.error(f"An unexpected error occurred while saving the file: {e}")
    
    logging.info("Process completed successfully.")

if __name__ == "__main__":
    main()

#--------------------------------------------------------------------------------------------
# End of script
#--------------------------------------------------------------------------------------------
# Note: The script is designed to be modular, with each function handling a specific task.
# This allows for easy debugging and testing of individual components.
# The script is also designed to be flexible, allowing for easy modification of parameters and file paths.
# The script is intended to be run in a Python environment with the necessary libraries installed.
# The script is designed to be run as a standalone program, but can also be imported as a module in other scripts.













