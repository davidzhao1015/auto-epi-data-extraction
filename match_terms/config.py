import os
from datetime import datetime

# === File and Folder Paths ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

LOG_DIR = os.path.join(BASE_DIR, "logs")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TEMPLATE_DIR = os.path.join(BASE_DIR, "example_input")

DEFAULT_LOG_FILE = os.path.join(LOG_DIR, "term_matching.log")
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
TIMESTAMPED_LOG_FILE = os.path.join(LOG_DIR, f"term_matching_{TIMESTAMP}.log")

# === Reported Terms Settings ===
DEFAULT_REPORTED_TERMS_FILE = os.path.join(TEMPLATE_DIR, "reported_terms_datahub.xlsb")
DEFAULT_REPORTED_SHEET = "Econ burden2"
DEFAULT_REPORTED_HEADER_ROW = 4
DEFAULT_REPORTED_COL_NAME = "Prospective vs Retro"

# === Standard Terms Settings ===
DEFAULT_STD_TERMS_FILE = os.path.join(TEMPLATE_DIR, "std_terms_engine_sheet.xlsx")
DEFAULT_STD_SHEET = "Engine"
DEFAULT_STD_HEADER_ROW = 0
DEFAULT_STD_COL_NAME = "Study Type"

# === Output Path ===
DEFAULT_OUTPUT_FILE = os.path.join(RESULTS_DIR, "Standardized_Terms_Results.xlsx")