import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

# --- SETTINGS ---
LOG_FILE = "seasonal_log.csv"
DATA_DIR = "starch_mango_database"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

st.set_page_config(page_title="Bio-Estate Dashboard", layout="wide")
st.title("🥭 Bio-Estate: Secure Pathogen Ledger")

# --- BLOCKCHAIN UTILITIES ---
def generate_hash(data_string):
    return hashlib.sha256(data_string.encode()).hexdigest()

def get_last_hash():
    if not os.path.exists(LOG_FILE):
        return "0000000000000000"
    try:
        df_temp = pd.read_csv(LOG_FILE)
        if not df_temp.empty:
            return str(df_temp.iloc[-1]['block_hash'])
        return "0000000000000000"
    except:
        return "0000000000000000"

# --- 1. SIDEBAR ---
st.sidebar.header("📡 Live Node Status")
if os.path.exists(LOG_FILE):
    try:
        df_sidebar = pd.read_csv(LOG_FILE)
        st.sidebar.metric("Total Blocks Secured", len(df_sidebar))
        st.sidebar.success("📍 Trinidad Node: ONLINE")
    except:
        st.sidebar.warning("Initializing Ledger...")
else:
    st.sidebar.warning("No ledger found yet.")

# --- 2. PATHOGEN ANALYSIS (Entry Hub) ---
st.header("🧬 Pathogen Analysis")
tab1, tab2 = st.tabs(["📁 File Upload", "⌨️ Manual DNA Entry"])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload .fasta or Image file", 
        type=['fasta', 'jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']
    )
    if uploaded_file is not None:
        save_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if "image" in uploaded_file.type or uploaded_file.name.lower().endswith(('jpg', 'jpeg', 'png')):
            st.image(save_path, width=250, caption="Preview of Evidence")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prev_hash = get_last_hash()
        current_hash = generate_hash(f"{timestamp}WEB_UPLOAD{save_path}{prev_hash}")
        
        if st.button("✅ Confirm & Secure File"):
            if not os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.write("timestamp,sender,filepath,previous_hash,block_hash\n")
            with open(LOG_FILE, "a") as log:
                log.write(f"{timestamp},WEB_USER,{save_path},{prev_hash},{current_hash}\n")
            st.success(f"Block {current_hash[:10]} Secured!")
            st.rerun()

with tab2:
    dna
    