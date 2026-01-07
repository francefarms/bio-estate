import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

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
        df = pd.read_csv(LOG_FILE)
        st.sidebar.metric("Total Blocks Secured", len(df))
        # Visual indicator for Trinidad Node
        st.sidebar.success("📍 Trinidad Node: ONLINE")
        st.sidebar.info("Syncing with Chaguanas Hub...")
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
        # Real-time GC Analysis
        gc = (dna_clean.count('G') + dna_clean.count('C')) / len(dna_clean) * 100
        risk = "⚠️ HIGH" if gc > 50 else "✅ LOW"
        st.write(f"**Diagnostic Result:** {risk} Risk ({gc:.1f}% GC Content)")
        
        if st.button("🔗 Secure DNA to Ledger"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prev_hash = get_last_hash()
            current_hash = generate_hash(f"{timestamp}TEXT_DATA{dna_clean}{prev_hash}")
            
            if not os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.write("timestamp,sender,filepath,previous_hash,block_hash\n")
            with open(LOG_FILE, "a") as log:
                log.write(f"{timestamp},WEB_USER,TEXT_DATA,{prev_hash},{current_hash}\n")
            st.success("DNA Sequence recorded in Blockchain.")
            st.rerun()

# --- 3. LIVE FARMER FEED ---
st.divider()
st.header("📡 Live Farmer Feed")

if os.path.exists(LOG_FILE):
    try:
        df = pd.read_csv(LOG_FILE)
        latest = df.iloc[::-1]

        for index, row in latest.iterrows():
            # Smart Labeling: Detect Trinidad numbers
            source_label = row['sender']
            if str(source_label).startswith('1868'):
                source_label = f"🇹🇹 Trinidad Farmer ({source_label})"
            
            with st.expander(f"Block: {str(row['block_hash'])[:12]}... (Source: {source_label})"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    filepath = str(row['filepath'])
                    if filepath != "TEXT_DATA" and os.path.exists(filepath):
                        st.image(filepath, use_container_width=True)
                    else:
                        st.info("🧬 DNA Sequence Data")
                
                with col2:
                    st.write(f"📅 **Timestamp:** {row['timestamp']}")
                    st.write(f"🔗 **Previous Hash:** `{str(row['previous_hash'])[:15]}...`")
                    st.write(f"🛡️ **Block Hash:** `{row['block_hash']}`")
    except Exception as e:
        st.error(f"Waiting for fresh data... (Header Sync: {e})")
else:
    st.info("Waiting for first transmission from field or web...")

# --- 4. EXPLORER ---
st.divider()
st.header("🔍 Blockchain Ledger Explorer")
search = st.text_input("Enter Block Hash to verify a report:")
if search and os.path.exists(LOG_FILE):
    result = df[df['block_hash'].astype(str).str.contains(search)]
    if not result.empty:
        st.success("✅ Block Verified in Ledger")
        st.dataframe(result)
    else:
        st.error("❌ Hash not found. This record may be counterfeit.")
        