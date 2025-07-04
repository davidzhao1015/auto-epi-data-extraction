# --------------------------------------------------------------------------------------------------------
# About this script:
# This script contains functions to parse and clean patient age data from a DataFrame.
# It includes functions:
# - Clean parameter names
# - Reshape the DataFrame
# - Normalize subtype names
# - Standardize age values
# - Parse interquartile range (IQR) values
# The script is designed to be modular and can be used as a utility in larger data processing pipelines.
# -------------------------------------------------------------------------------------------------------




# === Clean (normalize) parameter names ===

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




# === Reshape the data frame ===

import pandas as pd
import numpy as np


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





# === Normalize subtype names ===

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




# === Standardize ages (mean, SD, median and IQR) ===

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






# === Parse interquartile range (IQR) values ===

import pandas as pd
import numpy as np

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