import logging 
import os
import utils.convert_text_to_table as convert
import pandas as pd

import utils.unify_epi_para as unify

from utils import parse_age_stats as parse_age # Importing parse_age_stats module for age statistics parsing




def main():
    #=== Enter the folder path for AI-generate output files ===
    chat_output_dict = input("Enter the folder path for AI-generate output files: ").strip()
    if not os.path.exists(chat_output_dict):
        logging.error(f"Folder not found: {chat_output_dict}")
        return
    if not os.path.isdir(chat_output_dict):
        logging.error(f"Path is not a directory: {chat_output_dict}")
        return
    
    #=== Enter the file extension for AI-generate output files ===
    file_extension = input("Enter the file extension for AI-generate output files (e.g., txt, csv): ").strip()

    #=== sEnter the target disease name ===
    target_disease_name = input("Enter the target disease name (eg. CMS): ").strip()
    if not target_disease_name:
        logging.error("Target disease name cannot be empty.")
        return
    
    #=== Get file list from the specified  ===
    input_files = convert.get_file_list(chat_output_dict, file_extension)
    logging.info(f"Found {len(input_files)} files with extension {file_extension} in {chat_output_dict}.")
    if not input_files:
        logging.error(f"No files found with extension {file_extension} in {chat_output_dict}")
        return

    ref_id_df = convert.get_ref_id_from_filename(input_files)
    parsed_text_file = convert.parse_text_file(input_files, "Autoimmune Encephalitis")
    chat_epi_df = convert.convert_dict_to_df(parsed_text_file)

    chat_df_reshaped = convert.reshape_dataframe(chat_epi_df)
    chat_df_mapped = convert.map_ref_to_dataframe(chat_df_reshaped, input_files)

    #=== Normalize the study start and end years ===
    chat_df_mapped['study start year'] = chat_df_mapped['study start year'].apply(
    lambda x: unify.parse_dates(x, is_start_year=True))
    chat_df_mapped['study end year'] = chat_df_mapped['study end year'].apply(
    lambda x: unify.parse_dates(x, is_start_year=False))

    #=== Re-order columns aligning with Data Hub ===
    # Add placeholder columns, "author", "study period (days)" and "study period (years)"
    chat_df_mapped['author'] = ""
    chat_df_mapped['study period (days)'] = ""
    chat_df_mapped['study period (years)'] = ""

    # Re-order columns to match the Data Hub format
    columns_order = [
        "Ref", "author", "publication year", "region",
        "country", "coverage area", "study design", "study population",
        "population characteristics", "data source type", "data source details",
        "study timeline type", "number of sites", "study start year",
        "study end year", "study period (days)", "study period (years)",
        "main ethnicity", "ethnicity details", "disease studied",
        "diagnosis method", "diagnosis criteria details",
        "disease phase", "cohort age group", "female  in cohort", "consanguinity"]
    
    chat_df_mapped = chat_df_mapped[columns_order]


    #=== Convert certain columns to numeric types ===
    numeric_columns = ["publication year", "number of sites"]
    
    for col in numeric_columns:
        if col in chat_df_mapped.columns:
            chat_df_mapped[col] = pd.to_numeric(chat_df_mapped[col], errors='coerce')
    

    #== Export the processed DataFrame to an Excel file ===
    chat_df_mapped.to_excel("results/output.xlsx", index=False)
    logging.info("Data processing completed. Output saved to output.xlsx.")




if __name__ == "__main__":
    main()
