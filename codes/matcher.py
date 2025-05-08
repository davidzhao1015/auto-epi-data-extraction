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