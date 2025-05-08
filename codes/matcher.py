#=================================================================================
# This script is to unify symptoms based on cosine similarity and fuzzy matching
#=================================================================================

import pandas as pd
import numpy as np
import os

from sklearn.feature_extraction.text import TfidfVectorizer # Term Frequency-Inverse Document Frequency (TF-IDF)
from sklearn.feature_extraction.text import CountVectorizer # CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity # Cosine similarity

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import logging




#-----------------------------------------------------------
# Cosine similarity method to unify symptoms
#-----------------------------------------------------------

def standardize_clinical_terms(reported_term, std_term_list):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from fuzzywuzzy import process
    import spacy
    import pandas as pd
    from collections import defaultdict

    nlp = spacy.load("en_core_web_md")

    # Sanity check for reported_term - it should be a non-empty string
    if not isinstance(reported_term, str) or not reported_term.strip():
        return None, 0

    cleaned_std_terms = [t for t in std_term_list if isinstance(t, str) and t.strip()]
    if not cleaned_std_terms:
        return reported_term, 0

    best_match_collection = defaultdict(list)

    # TF-IDF Matching
    try:
        all_terms = cleaned_std_terms + [reported_term]
        tfidf_matrix = TfidfVectorizer().fit_transform(all_terms)
        similarity_matrix = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:])
        max_score = similarity_matrix.max()
        cosine_score = max_score * 100
        if max_score >= 0.7:
            best_match_idx = similarity_matrix.argmax()
            best_match = cleaned_std_terms[best_match_idx]
        else:
            best_match = reported_term
        best_match_collection[best_match].append(cosine_score)
    except Exception as e:
        print(f"[TF-IDF] Skipped due to error: {e}")

    # Fuzzy Matching
    try:
        best_match_fuzzy, fuzzy_score = process.extractOne(reported_term, cleaned_std_terms)
        if fuzzy_score >= 80:
            best_match_collection[best_match_fuzzy].append(fuzzy_score)
        else:
            best_match_collection[reported_term].append(fuzzy_score)
    except Exception as e:
        print(f"[Fuzzy] Skipped due to error: {e}")

    # Semantic Similarity
    try:
        reported_doc = nlp(reported_term)
        best_score = -1
        best_match_semantic = reported_term
        for std_term in cleaned_std_terms:
            std_doc = nlp(std_term)
            if reported_doc.vector_norm == 0 or std_doc.vector_norm == 0:
                continue
            score = reported_doc.similarity(std_doc)
            if score > best_score:
                best_score = score
                best_match_semantic = std_term
        semantic_score = best_score * 100
        if best_score >= 0.7:
            best_match_collection[best_match_semantic].append(semantic_score)
        else:
            best_match_collection[reported_term].append(semantic_score)
    except Exception as e:
        print(f"[Semantic] Skipped due to error: {e}")

    if not best_match_collection:
        return reported_term, 0

    best_match_df = pd.DataFrame([
        {"Standardized": k, "Score": sum(v)/len(v), "Count": len(v)}
        for k, v in best_match_collection.items()
    ])
    if best_match_df.empty:
        return reported_term, 0

    best_match_df.sort_values(by="Score", ascending=False, inplace=True)

    print("Best match collection:")
    print(best_match_df)
    print("Best match collection end.")

    if best_match_df["Count"].max() >= 3:
        return best_match_df[best_match_df["Count"] >= 2]["Standardized"].iloc[0], "sure match"
    else:
        return best_match_df.iloc[0]["Standardized"], "maybe match"
    

#-----------------------------------------------------------
# Load reported terms and standard terms
#-----------------------------------------------------------

def load_reported_terms(file_path, sheet_name, header_row, col_name):
    if file_path.endswith('.xlsb'):
        df = pd.read_excel(file_path, 
                           sheet_name=sheet_name, 
                           header=header_row, 
                           engine='pyxlsb',
                           na_values=[], keep_default_na=False) # Prevent "NA" from being read as NaN
    else:
        df = pd.read_excel(file_path, 
                           sheet_name=sheet_name, 
                           header=header_row,
                           na_values=[], keep_default_na=False) # Prevent "NA" from being read as NaN
    reported_terms = df[col_name]
    return reported_terms

def load_std_terms(file_path, sheet_name, header_row, col_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    std_terms = df[col_name].to_list()
    std_terms = [term for term in std_terms if isinstance(term, str) and term.strip()]  # Keep only non-empty strings
    std_terms = list(set(std_terms))  # Remove duplicates
    return std_terms

def save_results_to_excel(results, file_path):
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        results.to_excel(writer, index=False)    

#-----------------------------------------------------------
# Main function to run the script
#-----------------------------------------------------------

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

#-----------------------------------------------------------
# End of script
#-----------------------------------------------------------


# import pandas as pd
# from io import StringIO

# # Simulated Excel/CSV input
# data = StringIO("Col1\nNA\nhello\nN/A")

# df = pd.read_csv(data, na_values=[], keep_default_na=False)
# print(df)

