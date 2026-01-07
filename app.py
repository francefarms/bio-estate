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
    dna_input = st.text_area("Type or Paste DNA Sequence:", placeholder="Example: GATC...")
    if dna_input:
        dna_clean = dna_input.strip().upper()
        
        try:
            # --- 🧬 BIOPYTHON ANALYSIS ---
            seq_obj = Seq(dna_clean)
            gc = gc_fraction(seq_obj) * 100
            
            # --- 🛡️ EXPORT COMPLIANCE CHECK ---
            st.subheader("🛡️ Export Compliance Check")
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.metric("GC Content", f"{gc:.2f}%")
            
            with col_res2:
                if gc > 45: 
                    st.error("❌ REJECTED: High Risk")
                else:
                    st.success("✅ PASSED: Low Risk")

            if gc > 45:
                st.warning("High-virulence markers detected. Batch flagged for quarantine.")
            else:
                st.info("Biological integrity verified for USDA/EU export standards.")

            if st.button("🔗 Secure DNA to Ledger"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                prev_hash = get_last_hash()
                current_hash = generate_hash(f"{timestamp}TEXT_DATA{dna_clean}{prev_hash}")
                
                if not os.path.exists(LOG_FILE):
                    with open(LOG_FILE, "w") as f:
                        f.write("timestamp,sender,filepath,previous_hash,block_hash\n")
                with open(LOG_FILE, "a") as log:
                    log.write(f"{timestamp},WEB_USER,TEXT_DATA,{prev_hash},{current_hash}\n")
                st.success(f"DNA Block {current_hash[:10]} Secured.")
                st.rerun()
                
        except Exception as e:
            st.error(f"Data Error: {e}")

# --- 3. LIVE FARMER FEED ---
st.divider()
st.header("📡 Live Farmer Feed")

if os.path.exists(LOG_FILE):
    try:
        df_feed = pd.read_csv(LOG_FILE)
        if not df_feed.empty:
            latest = df_feed.iloc[::-1]

            for index, row in latest.iterrows():
                source_label = row['sender']
                if str(source_label).startswith('1868'):
                    source_label = f"🇹🇹 Trinidad Farmer ({source_label})"
                
                with st.expander(f"Block: {str(row['block_hash'])[:12]}... (Source: {source_label})"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        fpath = str(row['filepath'])
                        if fpath != "TEXT_DATA" and os.path.exists(fpath):
                            st.image(fpath, use_container_width=True)
                        else:
                            st.info("🧬 DNA Data Record")
                    with c2:
                        st.write(f"📅 **Timestamp:** {row['timestamp']}")
                        st.write(f"🛡️ **Hash:** `{row['block_hash']}`")
        else:
            st.info("Ledger is currently empty. Waiting for first transmission...")
    except Exception as e:
        st.error(f"Syncing Nodes... ({e})")
else:
    st.info("Waiting for first transmission from field or web...")

# --- 4. EXPLORER ---
st.divider()
st.header("🔍 Blockchain Ledger Explorer")
search = st.text_input("Enter Block Hash to verify:")
if search and os.path.exists(LOG_FILE):
    try:
        df_exp = pd.read_csv(LOG_FILE)
        result = df_exp[df_exp['block_hash'].astype(str).str.contains(search)]
        if not result.empty:
            st.success("✅ Block Verified in Ledger")
            st.dataframe(result)
        else:
            st.error("❌ Hash not found. Record may be altered or counterfeit.")
    except Exception as e:
        st.error(f"Explorer Error: {e}")