#-----------------------------------------------------------
# Load libraries
#-----------------------------------------------------------

import pandas as pd
import numpy as np
import os

from sklearn.feature_extraction.text import TfidfVectorizer # Term Frequency-Inverse Document Frequency (TF-IDF)
from sklearn.feature_extraction.text import CountVectorizer # CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity # Cosine similarity

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import logging
import os
from datetime import datetime

from match_terms.io_utils import load_reported_terms, load_std_terms, save_results_to_excel
from match_terms.matcher import standardize_clinical_terms

#-----------------------------------------------------------
# Main function to load data, process terms, and save results
#-----------------------------------------------------------


def main():
    # Set up logging
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = f"logs/term_matching_{timestamp}.log"

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_path),
                                  logging.StreamHandler()]) # Log to both file and console
    
    logging.info("Starting the term matching script...")

    try_example = input("Do you want to see an example of the input data? (yes/no): ").strip().lower()
    
    if try_example == 'yes':
        reported_terms_file = "example_input/reported_terms_datahub.xlsb"
        reported_terms_sheet = "Econ burden2"
        reported_terms_header_row = 4
        reported_terms_col_name = "Prospective vs Retro"

        std_terms_file = "example_input/std_terms_engine_sheet.xlsx"
        std_terms_sheet = "Engine"
        std_terms_header_row = 0
        std_terms_col_name = "Study Type"
    else:
        # Load reported terms and standard terms
        reported_terms_file = input("Enter the file path for reported terms: ").strip()

        reported_terms_sheet = input("Enter the sheet name for reported terms: ").strip()
        reported_terms_header_row = int(input("Enter the header row number for reported terms: ").strip())
        reported_terms_col_name = input("Enter the column name for reported terms: ").strip()
        
        # Load standard terms
        std_terms_file = input("Enter the file path for standard terms: ").strip()
        std_terms_sheet = input("Enter the sheet name for standard terms: ").strip()
        std_terms_header_row = int(input("Enter the header row number for standard terms: ").strip())
        std_terms_col_name = input("Enter the column name for standard terms: ").strip()

    # Output file path    
    output_file_path = input("Enter the output file path for results: ").strip()
    if not output_file_path:
        output_file_path = "results/standardized_terms.xlsx"
        logging.info(f"No output file path provided. Using default: {output_file_path}")

    # Load reported terms and standard terms
    logging.info("Loading reported terms...")
    reported_terms = load_reported_terms(reported_terms_file, reported_terms_sheet, 
                                         reported_terms_header_row, reported_terms_col_name)
    logging.info(f"Reported terms loaded: {len(reported_terms)} entries")
    
    logging.info("Loading standard terms...")
    std_terms = load_std_terms(std_terms_file, std_terms_sheet, 
                               std_terms_header_row, std_terms_col_name)
    logging.info(f"Standard terms loaded: {len(std_terms)} entries")


    # Process each reported term
    logging.info("Matching reported terms to standard terms...")
    results = []
    for term in reported_terms:
        try:
            match, count = standardize_clinical_terms(term, std_terms)
            results.append({"Reported_Term": term, 
                            "Standardized_Term": match, 
                            "Count": count})
        except Exception as e:
            print(f"Error processing term '{term}': {e}")
            results.append({"Reported_Term": term, 
                            "Standardized_Term": "error", 
                            "Count": 0})
    logging.info("Matching completed.")    

    results_df = pd.DataFrame(results)

    # Save results to Excel
    save_results_to_excel(results_df, output_file_path)
    logging.info(f"Results saved to {output_file_path}")
    print("Script completed successfully.")

if __name__ == "__main__":
    main()
