import logging 
import os
import utils.convert_text_to_table as convert
import pandas as pd

import utils.unify_epi_para as unify

from utils import parse_age_stats as parse_age # Importing parse_age_stats module for age statistics parsing




def main():
    # Enter the folder path for AI-generate output files
    chat_output_dict = input("Enter the folder path for AI-generate output files: ").strip()
    if not os.path.exists(chat_output_dict):
        logging.error(f"Folder not found: {chat_output_dict}")
        return
    if not os.path.isdir(chat_output_dict):
        logging.error(f"Path is not a directory: {chat_output_dict}")
        return
    
    # Enter the file extension for AI-generate output files
    file_extension = input("Enter the file extension for AI-generate output files (e.g., .txt, .csv): ").strip()

    # Enter the target disease name
    target_disease_name = input("Enter the target disease name: ").strip()
    if not target_disease_name:
        logging.error("Target disease name cannot be empty.")
        return
    
    # *Enter the subtype parameter list to drop 
    # subtype_parameter_list = input("Enter the subtype parameter list (comma-separated): ").strip()
    # subtype_parameters = subtype_parameter_list.split(",") if subtype_parameter_list else []
    # subtype_parameters2 = [param.strip() for param in subtype_parameters if param.strip()]
    # if not subtype_parameter_list:
    #     logging.error("Subtype parameter list cannot be empty.")
    #     return
    # logging.info(f"Subtype parameters to drop: {subtype_parameters2}")
    
    # Get file list from the specified directory
    input_files = convert.get_file_list(chat_output_dict, file_extension)
    logging.info(f"Found {len(input_files)} files with extension {file_extension} in {chat_output_dict}.")
    if not input_files:
        logging.error(f"No files found with extension {file_extension} in {chat_output_dict}")
        return

    ref_id_df = convert.get_ref_id_from_filename(input_files)
    parsed_text_file = convert.parse_text_file(input_files, "Autoimmune Encephalitis")
    chat_epi_df = convert.convert_dict_to_df(parsed_text_file)


    # *Drop subtype-specific parameters from the DataFrame - a crucial step
    # chat_df_dropped = convert.drop_subtype_specific_parameters(chat_epi_df, subtype_parameters2)
    # chat_df_dropped2 = convert.clean_parameter_names(chat_df_dropped)
    chat_df_reshaped = convert.reshape_dataframe(chat_epi_df)
    chat_df_mapped = convert.map_ref_to_dataframe(chat_df_reshaped, input_files)

    # Unify numeric values in study demographic parameters, including study duration, follow-up period, female percentage in cohort
    # chat_df_duration = chat_df_mapped.copy()
    # chat_df_duration[['study duration start', 'study duration end']] = chat_df_mapped['study duration'].apply(
    #     lambda x: pd.Series(unify.split_duration(x))
    # )

    # chat_df_duration['study duration start'] = chat_df_duration['study duration start'].apply(
    # lambda x: unify.parse_dates(x, is_start_year=True))
    # chat_df_duration['study duration end'] = chat_df_duration['study duration end'].apply(
    # lambda x: unify.parse_dates(x, is_start_year=False))

    chat_df_mapped.to_excel("results/output_unified_duration.xlsx", index=False)
    logging.info("Data processing completed. Output saved to output.xlsx.")




if __name__ == "__main__":
    main()
