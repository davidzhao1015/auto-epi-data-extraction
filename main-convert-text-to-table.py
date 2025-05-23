import logging 
import os
import utils.convert_text_to_table as convert
import pandas as pd




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
    
    # Enter the subtype parameter list to drop
    subtype_parameter_list = input("Enter the subtype parameter list (comma-separated): ").strip()
    if not subtype_parameter_list:
        logging.error("Subtype parameter list cannot be empty.")
        return
    
    input_files = convert.get_file_list(chat_output_dict, file_extension)

    ref_id_df = convert.get_ref_id_from_filename(input_files)

    parsed_text_file = convert.parse_text_file(input_files, "Autoimmune Encephalitis")

    chat_epi_df = convert.convert_dict_to_df(parsed_text_file)

    chat_df_dropped = convert.drop_subtype_specific_parameters(chat_epi_df, subtype_parameter_list)

    chat_df_dropped2 = convert.clean_parameter_names(chat_df_dropped)

    chat_df_reshaped = convert.reshape_dataframe(chat_df_dropped2)

    chat_df_mapped = convert.map_ref_to_dataframe(chat_df_reshaped, input_files)

    chat_df_mapped.to_excel("results/output.xlsx", index=False)
    print("Data processing completed. Output saved to output.xlsx.")



if __name__ == "__main__":
    main()
