import pandas as pd
import numpy as np
import os

from sklearn.feature_extraction.text import TfidfVectorizer # Term Frequency-Inverse Document Frequency (TF-IDF)
from sklearn.feature_extraction.text import CountVectorizer # CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity # Cosine similarity

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import logging


def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("term_matching.log"),
                                  logging.StreamHandler()])
    logging.info("Starting the term matching script...")
    
    # Load reported terms and standard terms
    logging.info("Loading reported terms...")
    reported_terms_file = input("Enter the file path for reported terms: ").strip() 
    reported_terms_sheet = input("Enter the sheet name for reported terms: ").strip()
    reported_terms_header_row = int(input("Enter the header row number for reported terms: ").strip())
    reported_terms_col_name = input("Enter the column name for reported terms: ").strip()
    
    reported_terms = load_reported_terms(reported_terms_file, reported_terms_sheet, 
                                         reported_terms_header_row, reported_terms_col_name)
    logging.info(f"Reported terms loaded: {len(reported_terms)} entries")

    logging.info("Loading standard terms...")
    std_terms_file = input("Enter the file path for standard terms: ").strip()
    std_terms_sheet = input("Enter the sheet name for standard terms: ").strip()
    std_terms_header_row = int(input("Enter the header row number for standard terms: ").strip())
    std_terms_col_name = input("Enter the column name for standard terms: ").strip()

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
    output_file_path = input("Enter the output file path for results: ").strip()
    save_results_to_excel(results_df, output_file_path)
    logging.info(f"Results saved to {output_file_path}")
    print("Script completed successfully.")

if __name__ == "__main__":
    main()
