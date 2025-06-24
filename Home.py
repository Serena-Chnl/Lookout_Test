# test/Home.py

import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import datetime
import nltk
import time # Import time for sleep

def download_nltk_resources() -> bool:
    """
    Downloads required NLTK resources for text processing.
    Returns True if successful, False otherwise.
    """
    resources_to_download = [
        # Only include resources that are problematic or explicitly used in the minimal example
        ('tokenizers/punkt', 'punkt'),
        ('tokenizers/punkt_tab', 'punkt_tab'), # This is the one we are focusing on
        ('corpora/stopwords', 'stopwords') # Also include stopwords as customer_profile needs it
    ]
    
    all_downloaded = True
    
    # Use a placeholder or toast for less intrusive feedback
    status_placeholder = st.empty() 
    status_placeholder.info("Checking/Downloading NLTK resources... This might take a moment.")
    
    for resource_path, download_name in resources_to_download:
        try:
            nltk.data.find(resource_path)
            # status_placeholder.text(f"NLTK resource '{download_name}' found locally.") # Optional: for debugging
        except LookupError:
            try:
                # Use st.toast for transient messages, and st.spinner for long operations
                with st.spinner(f"Downloading NLTK resource '{download_name}'..."):
                    nltk.download(download_name, quiet=True)
                st.toast(f"Downloaded '{download_name}'!", icon="✅")
            except Exception as e:
                status_placeholder.error(f"Error downloading NLTK resource '{download_name}': {e}")
                st.toast(f"Failed to download '{download_name}'!", icon="❌")
                all_downloaded = False
    
    if all_downloaded:
        status_placeholder.success("All NLTK resources downloaded/verified!")
        # Add a short sleep to ensure the download fully settles before rendering other pages
        time.sleep(1) # Give it 1 second to settle
    else:
        status_placeholder.warning("Some NLTK resources could not be downloaded. Functionality might be limited.")
    return all_downloaded

# --- Define Base Directory ---
BASE_DIR = Path(__file__).resolve().parent
# Assuming logos and data are in the parent directory for this test setup
LOOKOUT_LOGO_PATH = BASE_DIR.parent / "lookout_logo_01.png"
DATA_FILE_PATH = BASE_DIR.parent / "Lookout_dataset_cleaned.csv"

# --- Page Configuration (Global) ---
page_icon = "🌆"
try:
    img_icon = Image.open(LOOKOUT_LOGO_PATH)
    page_icon = img_icon
except Exception as e:
    st.warning(f"Cannot use '{LOOKOUT_LOGO_PATH.name}' as page icon: {e}. Using default emoji icon.")

st.set_page_config(
    page_title="A'DAM LOOKOUT Test Insights",
    page_icon=page_icon,
    layout="wide"
)

# --- Header (Simplified) ---
st.title("Test Dashboard - Home")
st.markdown("This mini-dashboard is for debugging NLTK `punkt_tab` issue.")

# --- Perform NLTK resource download/verification at app startup ---
# This ensures that all necessary NLTK data is available before any page potentially uses it.
# Check if the download has already been attempted in the current session
if 'nltk_resources_downloaded' not in st.session_state:
    if download_nltk_resources():
        st.session_state.nltk_resources_downloaded = True
    else:
        st.session_state.nltk_resources_downloaded = False
        # If download fails, you might want to stop the app or disable NLTK-dependent features
        # For now, we'll let it proceed with a warning.

# --- Data Loading (Simplified) ---
@st.cache_data
def load_cleaned_data(file_path):
    """Loads the pre-processed CSV data and converts the 'Time' column."""
    try:
        df = pd.read_csv(file_path)
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        
        required_cols = ['Name', 'Rating', 'Time', 'Review', 'Language', 'compound', 'label']
        if not all(col in df.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in df.columns]
            st.error(f"CRITICAL ERROR: Cleaned data is missing required columns: {', '.join(missing_cols)}. Please ensure the data is complete.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"CRITICAL ERROR: The data file '{file_path}' was not found. Please ensure it's in the main project directory.")
        return None
    except Exception as e:
        st.error(f"CRITICAL ERROR: An unexpected error occurred while loading the data: {e}")
        return None

# --- Initialize Session State for Data ---
if 'processed_data' not in st.session_state:
    df = load_cleaned_data(DATA_FILE_PATH)
    if df is not None:
        st.session_state.processed_data = df
    else:
        st.session_state.processed_data = None
        st.error("Failed to load pre-processed data. The dashboard cannot operate.")
        st.stop() # Stop execution if critical data is missing

st.info("The processed dataset is loaded. Navigate to 'customer_profile' in the sidebar.")
st.markdown("---")