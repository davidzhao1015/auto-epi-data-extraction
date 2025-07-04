#==============================================================================
# This script is used to parse subtype-specific patient ages for eco burden data 
#==============================================================================

import os
import re
import numpy as np
import pandas as pd
import pyxlsb

# #----------------------------------------------------------------
# # List files in the folder
# #----------------------------------------------------------------

# # Change the working directory to the folder containing the txt files 
# os.chdir('/Users/xinzhao/ISMS_Work/Project_AIE/Working/chatgpt_outputs/chatgpt_output_epi/batch_3_eco') 

# # List all files in the directory
# file_list_epi = [] 
# for file in os.listdir():
#     if file.endswith("epi_v.txt"):
#         file_list_epi.append(file)
#     else:
#         print(f"File {file} is not a txt file.") 

# # Sort the file list
# file_list_epi.sort() 
# print(file_list_epi)

# print(len(file_list_epi)) # Check the number of files in the list

# # Convert the list to a dictionary 
# file_dict_epi = {i:file_list_epi[i] for i in range(0, len(file_list_epi))}
# print(file_dict_epi)

# # file_dict_epi_df = pd.DataFrame(list(file_dict_epi.items()), columns = ['File', 'Ref']) 
# # file_dict_epi_df['Ref'] = file_dict_epi_df['Ref'].str.split("_").str[1]
# # file_dict_epi_df.to_csv("file_dict_epi.csv", index=False)


# #---------------------------------------------------------------
# # Read in each txt file, and write the contents to data frames 
# #---------------------------------------------------------------

# chat_dict_epi = {} # Create a dictionary to store the chat output
# for key0, value0 in file_dict_epi.items():
#     print(key0, value0)
#     # Remove the line with "Quote(s)" in the txt file 
#     with open(f"{value0}", "r") as f:
#         lines = f.readlines()
#         lines = [line for line in lines if 'Line(s)' not in line]
#         lines = [line for line in lines if 'Section' not in line] 
#         lines = [line for line in lines if "Quote(s)" not in line]
#         # Skip empty lines
#         lines = [line for line in lines if line != '\n']
#         lines = [line for line in lines if line != ""]
#         lines = [line.strip("\t") for line in lines] # Remove the leading and trailing tabs which is critical for the split function
      
#         chat_key = key0 # key is the index of the file
#         chat_dict_epi[chat_key] = {} # Create a nested dictionary for each txt file 

#         for line in lines:
#             # print(line)
#             if ":" in line and re.match(r'^\d+', line): 
#                 key1, value1 = line.split(":", 1)
#                 # print(key1, f'the value is {value1}')

#                 if "Age of Patients by Subtype" in key1:
#                     ind = lines.index(line) + 1 
#                     while not re.match(r"^\d+", lines[ind]): 
#                         key2, value2 = lines[ind].split(":", 1)
#                         print(key2, f'the value is {value2}') # Check the key and value pairs

#                         keywords = ['Mean', 'Median', 'SD', 'IQR', 'Subtype', 'Standard Deviation']
#                         if all(keyword not in key2 for keyword in keywords): 
#                             value3 = key2
#                             key3 = key1 + " " + "Subtype" + " " + str(ind) # Add a unique identifier to the key
#                             chat_dict_epi[chat_key][key3] = value3.strip()
#                         else:
#                             key3 = key1 + " " + key2.strip() + " " + str(ind) # Add a unique identifier to the key
#                             chat_dict_epi[chat_key][key3] = value2.strip()
#                             print(chat_dict_epi[chat_key])
#                         ind += 1
#                     else:
#                         continue
#                 else:
#                     continue
#             else:
#                 continue    

# print(len(chat_dict_epi)) # Check the number of files read in
# print(chat_dict_epi[2]) 



# #---------------------------------------------------------------
# # Convert the dictionary to a data frame
# #--------------------------------------------------------------- 
# chat_df = pd.DataFrame(columns = ["File", "Parameter", "Value"])
# rows = []

# for key4, value4 in chat_dict_epi.items():
#     for parameter, cell in value4.items():
#         rows.append({'File': key4, 'Parameter': parameter, 'Value': cell})

# chat_df = pd.concat([chat_df, pd.DataFrame(rows)], ignore_index=True)   

# # Export the data frame to a csv file
# chat_df.to_csv("parsed_patient_age.csv", index=False)

chat_df.head(10) # Check the first 10 rows of the data frame    

#---------------------------------------------------------------
# *Unify Parameter column
#---------------------------------------------------------------

# # *Remove "22.    Age of Patients by Subtype" from the Parameter column
# chat_df2 = chat_df.copy()
# chat_df2['Parameter'] = chat_df['Parameter'].str.replace(r'22.\t*Age of Patients by Subtype', "", regex=True)

# chat_df2.head(10)

# # Remove •\t from the Parameter column
# chat_df2['Parameter'] = chat_df2['Parameter'].str.replace(r'•\t', "", regex=True)
# chat_df2.head(10)

# # Remove digits from the Parameter column
# chat_df3 = chat_df2.copy()
# chat_df3['Parameter'] = chat_df2['Parameter'].str.replace(r'\d*', "", regex=True)

# chat_df3.head(10)

# # Unify the names in Parameter column
# chat_df3['Parameter'].unique()

# chat_df3['Parameter'] = chat_df3['Parameter'].str.strip()
# chat_df3['Parameter'].unique()

# # Replace Standard Deviation with SD
# chat_df3['Parameter'] = chat_df3['Parameter'].str.replace("Standard Deviation", "SD")
# chat_df3['Parameter'].unique()

chat_df3.head(10) # Check the first 10 rows of the data frame   



import pandas as pd
import re

def clean_age_parameter_name(df, param='Parameter'):
    """
    Clean the parameter name by removing leading and trailing spaces and special characters.
    The function exclusively handles the 'Age of Patients by Subtype' parameter.
    """
    df2 = df.copy()
    df2[param] = df['Parameter'].str.replace(r'22.\t*Age of Patients by Subtype', "", regex=True) 
    df2[param] = df2[param].str.replace(r'•\t', "", regex=True)
    df2[param] = df2[param].str.replace(r'\d*', "", regex=True)
    df2[param] = df2[param].str.strip()
    df2[param] = df2[param].str.replace('Standard Deviation', 'SD')

    return df2


# # Test case
# df_param_cleaned = clean_age_parameter_name(chat_df)
df_param_cleaned.head(30)


#---------------------------------------------------------------
# Reshape the data frame
#---------------------------------------------------------------
chat_df4 = chat_df3.copy()

# Create a new column for Subtype
subtype_list = []

for i in range(0, len(chat_df4)):
    if chat_df4['Parameter'][i] == "Subtype":
        subtype_list.append(chat_df4['Value'][i])
        
        index = i+1
        while chat_df4['Parameter'][index] != "Subtype":
            subtype_list.append(chat_df4['Value'][i])
            index += 1
    else:
        continue

chat_df4['Subtype'] = subtype_list
chat_df4.head(30)

# Drop row with Parameter = Subtype
chat_df5 = chat_df4[chat_df4.Parameter != "Subtype"] 
chat_df5.head(30)

# Make long table wide 
chat_df6 = chat_df5.pivot(index=('File', 'Subtype'), columns='Parameter', values='Value').reset_index()
chat_df6.head(30)

# Export the data frame to a csv file
chat_df6.to_csv("parsed_patient_age_wide.csv", index=False)

chat_df6.head(10) # Check the first 30 rows of the data frame




def pivot_age_dataframe(df):
    """
    Reshape the DataFrame to have 'File' and 'Subtype' as index and 'Parameter' as columns.
    The function exclusively handles the 'Age of Patients by Subtype' parameter.
    It returns a new DataFrame with the reshaped data.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing patient age data.
    Returns:
    pd.DataFrame: A new DataFrame with 'File' and 'Subtype' as index and 'Parameter' as columns.
    """
    df2 = df.copy()

    # Create a new column for Subtype
    subtype_list = [None] * len(df2)  # Initialize with None values
    current_subtype = None
    
    for i in range(len(df2)):
        if df2.iloc[i]['Parameter'] == "Subtype":
            current_subtype = df2.iloc[i]['Value']
            # Don't assign subtype to the "Subtype" row itself
        else:
            # Assign current subtype to non-subtype rows
            if current_subtype is not None:
                subtype_list[i] = current_subtype

    df2['Subtype'] = subtype_list

    # Drop rows with Parameter = 'Subtype' and rows without subtype assignment
    df3 = df2[(df2['Parameter'] != 'Subtype') & (df2['Subtype'].notna())]

    # Check if we have any data left after filtering
    if df3.empty:
        print("Warning: No data remaining after filtering. Check input data format.")
        return pd.DataFrame()

    # Make long table wide 
    try:
        df4 = df3.pivot(index=['File', 'Subtype'], 
                           columns='Parameter', 
                           values='Value').reset_index()
        return df4
    except Exception as e:
        print(f"Error during pivot operation: {e}")
        print("Available columns:", df3.columns.tolist())
        print("Unique parameters:", df3['Parameter'].unique() if 'Parameter' in df3.columns else "Parameter column missing")
        return pd.DataFrame()

# Test the pivot function
# df_pivoted = pivot_age_dataframe(df_param_cleaned)
# df_pivoted.head(30)


#---------------------------------------------------------------
# Standardize the data
#---------------------------------------------------------------

# Remove •\t from Subtype column
chat_df6['Subtype'] = chat_df6['Subtype'].str.replace(r'•\t', "", regex=True)
chat_df6['Subtype'] = chat_df6['Subtype'].str.strip()
chat_df6['Subtype'].unique()

import pandas as pd


def clean_subtype_name(df, subtype_column='Subtype'):
    """
    Clean the subtype names by removing leading and trailing spaces and special characters.
    This function handles various formatting issues commonly found in subtype data.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing patient age data.
    subtype_column (str, optional): The name of the column containing subtype information. 
                                   Defaults to 'Subtype'.
    
    Returns:
    pd.DataFrame: A new DataFrame with cleaned subtype names.
    
    Raises:
    KeyError: If the specified subtype_column doesn't exist in the DataFrame.
    """
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if subtype_column not in df.columns:
        raise KeyError(f"Column '{subtype_column}' not found in DataFrame. "
                      f"Available columns: {list(df.columns)}")
    
    df2 = df.copy()
    
    # Skip processing if column is empty or all NaN
    if df2[subtype_column].isna().all():
        print(f"Warning: Column '{subtype_column}' contains only NaN values")
        return df2
    
    # Clean subtype names with comprehensive pattern matching
    # Remove bullet points and tabs
    df2[subtype_column] = df2[subtype_column].str.replace(r'•\t', "", regex=True)
    
    # Remove other common bullet point patterns
    df2[subtype_column] = df2[subtype_column].str.replace(r'[•·‣▪▫]\s*', "", regex=True)
    
    # Remove leading/trailing whitespace and normalize internal spaces
    df2[subtype_column] = df2[subtype_column].str.strip()
    df2[subtype_column] = df2[subtype_column].str.replace(r'\s+', " ", regex=True)
    
    # Remove any remaining tab characters
    df2[subtype_column] = df2[subtype_column].str.replace(r'\t', "", regex=True)
    
    # Convert empty strings to NaN for consistency
    df2[subtype_column] = df2[subtype_column].replace('', np.nan)
    
    return df2

# Test case
# df_cleaned = clean_subtype_name(chat_df6, subtype_column='Subtype')

#---------------------------------------------------------------
# Standardize the Mean, Median, and SD columns
#---------------------------------------------------------------

def standardize_age(age, verbose=False):
    """
    Standardize age values by converting various text formats to numeric years.
    
    Parameters:
    age: Age value in various formats (string, numeric, or NaN)
    verbose (bool): If True, print debugging information
    
    Returns:
    float: Age in years, or np.nan if cannot be parsed
    
    Examples:
    - "25.5" -> 25.5
    - "30 years" -> 30.0
    - "6 months" -> 0.5
    - "25 years 6 months" -> 25.5
    - "NR" -> np.nan
    """
    # Handle NaN and None inputs
    if pd.isna(age) or age is None:
        return np.nan
    
    age_str = str(age).strip().lower()
    
    # Handle "not reported" cases
    if age_str in ["nr", "not reported", "na", "n/a", "", "nan"]:
        return np.nan
    
    # Try to convert simple numeric values first
    try:
        # Check if it's already a number
        numeric_age = float(age_str)
        # Reasonable age range check (0-150 years)
        if 0 <= numeric_age <= 150:
            return numeric_age
        else:
            if verbose:
                print(f"Warning: Age {numeric_age} is outside reasonable range (0-150)")
            return np.nan
    except ValueError:
        pass  # Continue to text parsing
    
    # Parse text containing age information
    if any(keyword in age_str for keyword in ['year', 'month', 'yr', 'mo']):
        if verbose:
            print(f"Parsing age text: {age_str}")
        
        total_years = 0.0
        
        # Extract years - handles: "25 years", "25 yrs", "25y", "25 yr"
        year_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?|y)\b',
            r'(\d+(?:\.\d+)?)\s*(?=\s*years?|\s*yrs?|\s*y\b)'
        ]
        
        for pattern in year_patterns:
            year_matches = re.findall(pattern, age_str)
            if year_matches:
                try:
                    total_years += float(year_matches[0])
                    break  # Use first successful match
                except ValueError:
                    continue
        
        # Extract months - handles: "6 months", "6 mos", "6m", "6 mo"
        month_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:months?|mos?|m)\b',
            r'(\d+(?:\.\d+)?)\s*(?=\s*months?|\s*mos?|\s*m\b)'
        ]
        
        for pattern in month_patterns:
            month_matches = re.findall(pattern, age_str)
            if month_matches:
                try:
                    months = float(month_matches[0])
                    if months <= 24:  # Reasonable check (up to 24 months)
                        total_years += months / 12.0
                        break
                except ValueError:
                    continue
        
        # Return result if we found something
        if total_years > 0:
            return round(total_years, 2)  # Round to 2 decimal places
        else:
            if verbose:
                print(f"Warning: Could not extract age from '{age_str}'")
            return np.nan
    
    # Try to extract any number from the string as last resort
    numbers = re.findall(r'\d+(?:\.\d+)?', age_str)
    if numbers:
        try:
            numeric_age = float(numbers[0])
            if 0 <= numeric_age <= 150:
                return numeric_age
            else:
                if verbose:
                    print(f"Warning: Extracted age {numeric_age} is outside reasonable range")
                return np.nan
        except ValueError:
            pass
    
    # If all else fails
    if verbose:
        print(f"Warning: Unable to parse age value: '{age}'")
    return np.nan    

        
# chat_df7 = chat_df6.copy()
# chat_df7['Mean'] = chat_df6['Mean'].apply(standardize_age)

# chat_df7['Median'] = chat_df6['Median'].apply(standardize_age)
# chat_df7['SD'] = chat_df6['SD'].apply(standardize_age)

# chat_df7.head(30)

# # Export the data frame to a csv file
# chat_df7.to_csv("parsed_patient_age_wide_2.csv", index=False)





#---------------------------------------------------------------
# Deal with IQR
#---------------------------------------------------------------

def parse_irq(iqr, verbose=False):
    """
    Parse interquartile range (IQR) values from text and convert them into a tuple of numeric values.

    Parameters:
    iqr (str): The IQR value in text format.
    verbose (bool): If True, print debugging information.

    Returns:
    tuple: A tuple (lower, upper) representing the IQR in numeric format, or (np.nan, np.nan) if invalid.

    Examples:
    - "25–30" -> (25.0, 30.0)
    - "25 - 30" -> (25.0, 30.0)
    - "25 to 30" -> (25.0, 30.0)
    - "NR" -> (np.nan, np.nan)
    """
    # Handle NaN and None inputs
    if pd.isna(iqr) or iqr is None:
        return (np.nan, np.nan)

    iqr_str = str(iqr).strip().lower()

    # Handle "not reported" cases
    if iqr_str in ["nr", "not reported", "na", "n/a", "", "nan"]:
        return (np.nan, np.nan)

    # Define delimiters for splitting IQR
    delimiters = ["–", "-", "to"]
    for delimiter in delimiters:
        if delimiter in iqr_str:
            try:
                # Split the IQR string using the delimiter
                lower, upper = iqr_str.split(delimiter, 1)
                lower = standardize_age(lower.strip())
                upper = standardize_age(upper.strip())

                # Ensure both values are numeric
                if pd.notna(lower) and pd.notna(upper):
                    return (lower, upper)
                else:
                    if verbose:
                        print(f"Warning: Invalid IQR values after parsing: '{lower}', '{upper}'")
                    return (np.nan, np.nan)
            except ValueError:
                if verbose:
                    print(f"Error: Unable to split IQR string '{iqr_str}' using delimiter '{delimiter}'")
                return (np.nan, np.nan)

    # If no valid delimiter is found
    if verbose:
        print(f"Warning: No valid delimiter found in IQR string: '{iqr_str}'")
    return (np.nan, np.nan)