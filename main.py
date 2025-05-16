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

from match_terms import config

#-----------------------------------------------------------
# Main function to load data, process terms, and save results
#-----------------------------------------------------------


def main():
    # Set up logging
    # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # LOG_DIR = f"logs/term_matching_{timestamp}.log"

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(config.TIMESTAMPED_LOG_FILE),
                                  logging.StreamHandler()]) # Log to both file and console
    
    logging.info("Starting the term matching script...")
    
    # Load reported terms and standard terms
    reported_terms_file = input("Enter the file path for reported terms (otherwise the default example will be used): ").strip() or config.DEFAULT_REPORTED_TERMS_FILE
    if not os.path.exists(reported_terms_file):
        logging.error(f"File not found: {reported_terms_file}")
        return

    reported_terms_sheet = input("Enter the sheet name for reported terms (otherwise the default example will be used): ").strip() or config.DEFAULT_REPORTED_SHEET
    if not reported_terms_sheet:
        logging.error("Sheet name cannot be empty.")
        return
    
    reported_terms_header_row = int(input("Enter the header row number for reported terms (otherwise the default example will be used): ").strip() or config.DEFAULT_REPORTED_HEADER_ROW) 
    if reported_terms_header_row < 0:
        logging.error("Header row number must be non-negative.")
        return
    
    reported_terms_col_name = input("Enter the column name for reported terms (otherwise the default example will be used): ").strip() or config.DEFAULT_REPORTED_COL_NAME
    if not reported_terms_col_name:
        logging.error("Column name cannot be empty.")
        return
        
    # Load standard terms
    std_terms_file = input("Enter the file path for standard terms (otherwise the default example will be used): ").strip() or config.DEFAULT_STD_TERMS_FILE
    if not os.path.exists(std_terms_file):
        logging.error(f"File not found: {std_terms_file}")
        return
    
    std_terms_sheet = input("Enter the sheet name for standard terms (otherwise the default example will be used): ").strip() or config.DEFAULT_STD_SHEET
    if not std_terms_sheet:
        logging.error("Sheet name cannot be empty.")
        return
    
    std_terms_header_row = int(input("Enter the header row number for standard terms (otherwise the default example will be used): ").strip() or config.DEFAULT_STD_HEADER_ROW) 
    if std_terms_header_row < 0:
        logging.error("Header row number must be non-negative.")
        return
    
    std_terms_col_name = input("Enter the column name for standard terms (otherwise the default example will be used): ").strip() or config.DEFAULT_STD_COL_NAME
    if not std_terms_col_name:
        logging.error("Column name cannot be empty.")
        return

    # Output file path    
    output_file_path = input("Enter the output file path for results: ").strip()
    if not output_file_path:
        logging.info(f"No output file path provided. Using default: {config.DEFAULT_OUTPUT_FILE}")

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
    save_results_to_excel(results_df, config.DEFAULT_OUTPUT_FILE)
    logging.info(f"Results saved to {config.DEFAULT_OUTPUT_FILE}")
    print("Script completed successfully.")

if __name__ == "__main__":
    main()
