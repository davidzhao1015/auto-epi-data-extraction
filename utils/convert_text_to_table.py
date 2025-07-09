#-------------------------------------------------------------------------------------------------
# About this script:
# This script is used to tabularize the AI chat output of the epidemiology data extracted for literature review.
# It includes functions to:
# - List files in a directory with a specified file extension
# - Extract reference IDs from filenames
# - Parse structured text files into a nested dictionary
# - Convert the nested dictionary into a DataFrame
# - Drop subtype-specific parameters from the DataFrame
# - Clean parameter names by removing special characters and converting to lowercase
# - Reshape the DataFrame to have 'File', 'Parameter', and 'Value'
# - Map reference IDs to the DataFrame based on the input files
# # The script is designed to be modular and can be used as a utility in larger data processing pipelines.
#-------------------------------------------------------------------------------------------------



import re
import pandas as pd
import numpy as np
import os

import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


import sys
from pathlib import Path




# === List files in the folder ===


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



# # Test case
# input_files = get_file_list("example_input/chatgpt_output_batch_testing", 'txt')
# print(input_files)


# === Extract reference ID from filenames ===

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

# # Test case
# print(input_files)

# ref_id_df = get_ref_id_from_filename(input_files)
# print(ref_id_df)






#=== Read Text Files into Data Frames ===

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
# parsed_text_files = parse_text_file(input_files, "Autoimmune Encephalitis")





#=== Convert the dictionary to a data frame ===
import re
import pandas as pd

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

    # Normalize Parameter names, by removing leading digits, periods, and brackets
    for row in rows:
        row['Parameter'] = re.sub(r'[^a-zA-Z\s]', '', row['Parameter']).strip().lower()

    return pd.DataFrame(rows)

# # Test case
# chat_df_epi = convert_dict_to_df(parsed_text_files)
# print(chat_df_epi.head(20))




#=== Drop subtype-specific parameters for separate processing ===

def drop_subtype_specific_parameters(chat_df, keywords=None):
    """
    Drop subtype-specific parameters from the DataFrame.

    Args:
        chat_df (pd.DataFrame): The DataFrame containing the parsed data.
        keywords (list, optional): A list of keywords to identify subtype-specific parameters.
                                   Parameters containing these keywords will be dropped.
                                   Matching is case-insensitive.

    Returns:
        pd.DataFrame: Filtered DataFrame with subtype-specific parameters dropped.
    """
    if keywords is None:
        keywords = ['Age', 'Patient Number']

    # Build regex pattern from keywords
    pattern = '|'.join(map(re.escape, keywords)) # Join keywords with '|'; re.escape to escape special characters

    # Filter out matching rows
    filtered_df = chat_df[~chat_df['Parameter'].str.contains(pattern, case=False, na=False)]

    return filtered_df

# # Test case
# keywords = ['Age of Patients','Patient Number of Autoimmune Encephalitis','Age of Diagnosis']
# chat_df_dropped = drop_subtype_specific_parameters(chat_df_epi, keywords=keywords)






#=== Subset subtype-specific parameters for separate processing ===

def subset_subtype_specific_parameters(chat_df, keywords=None):
    """
    Subset subtype-specific parameters from the DataFrame.

    Args:
        chat_df (pd.DataFrame): The DataFrame containing the parsed data.
        keywords (list, optional): A list of keywords to identify subtype-specific parameters.
                                   Parameters containing these keywords will be retained.
                                   Matching is case-insensitive.

    Returns:
        pd.DataFrame: Filtered DataFrame with only subtype-specific parameters retained.
    """
    if keywords is None:
        keywords = ['Age', 'Patient Number']

    # Build regex pattern from keywords
    pattern = '|'.join(map(re.escape, keywords))  # Join keywords with '|'; re.escape to escape special characters

    # Filter matching rows
    filtered_df = chat_df[chat_df['Parameter'].str.contains(pattern, case=False, na=False)]

    return filtered_df






#=== Clean parameter names, remove special characters ===

def clean_parameter_names(chat_df):
    """
    Clean the 'Parameter' column in a DataFrame:
    - Remove leading digits, periods, and brackets
    - Strip extra whitespace
    - Convert to lowercase

    Args:
        chat_df (pd.DataFrame): Input DataFrame with a 'Parameter' column.

    Returns:
        pd.DataFrame: A cleaned copy of the input DataFrame.
    """
    df = chat_df.copy()
    
    # Remove leading digits, optional period or closing bracket, and whitespace
    df['Parameter'] = df['Parameter'].str.replace(r'^\d+[\.\]]*\s*', '', regex=True)

    # Trim whitespace and lowercase
    df['Parameter'] = df['Parameter'].str.strip().str.lower()

    return df

# # Test case
# chat_df_dropped2 = clean_parameter_names(chat_df_dropped)
# print(chat_df_dropped2.head(20))





# === Reshape the data frame ===

def reshape_dataframe(chat_df):
    """
    Reshape the DataFrame to have 'File', 'Parameter', and 'Value' columns.

    Args:
        chat_df (pd.DataFrame): The DataFrame containing the parsed data.

    Returns:
        pd.DataFrame: Reshaped DataFrame with 'File', 'Parameter', and 'Value' columns.
    """
    reshaped_df = chat_df.pivot(index='File', columns='Parameter', values='Value').reset_index() 
    return reshaped_df

# # Test case
# chat_df_reshaped = reshape_dataframe(chat_df_dropped2)
# print(chat_df_reshaped.head(20))





# === Map Ref to the data frame ===

def map_ref_to_dataframe(chat_df, input_files):
    """
    Map reference IDs to the DataFrame based on the input files.
    
    Args:
        chat_df (pd.DataFrame): The DataFrame containing the parsed data.
        input_files (dict): A dictionary of files with the specified extension.
        
    Returns:
        pd.DataFrame: A DataFrame with an additional 'Ref' column.
    """
    chat_df2 = chat_df.copy()

    file_ref_df = get_ref_id_from_filename(input_files)

    chat_df2 = chat_df2.merge(file_ref_df, on='File', how='left')

    return chat_df2

# # Test case
# chat_df_mapped = map_ref_to_dataframe(chat_df_reshaped, input_files)
# print(chat_df_mapped.head(20))



