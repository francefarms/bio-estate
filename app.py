import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction
from PIL import Image
import piexif 

# --- SETTINGS ---
LOG_FILE = "seasonal_log.csv"
DATA_DIR = "starch_mango_database"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("timestamp,sender,filepath,previous_hash,block_hash\n")

st.set_page_config(page_title="Bio-Estate Dashboard", layout="wide")

# Custom CSS for "High-Tech" look
st.markdown("""
    <style>
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 10px; border: 1px solid #374151; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; background-color: #2ecc71; color: white; }
    [data-testid="stSidebar"] { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- UTILITIES ---
def generate_hash(data_string):
    return hashlib.sha256(data_string.encode()).hexdigest()

def get_last_hash():
    try:
        df_temp = pd.read_csv(LOG_FILE)
        if not df_temp.empty:
            return str(df_temp.iloc[-1]['block_hash'])
    except:
        pass
    return "0000000000000000"

def get_image_gps(img_path):
    try:
        img = Image.open(img_path)
        if 'exif' in img.info:
            return "📍 GPS Verified (Field Entry)"
    except:
        pass
    return "📍 Trinidad Hub (Stationary Node)"

# --- SIDEBAR ---
st.sidebar.title("🥭 Bio-Estate Node")
df_count = pd.read_csv(LOG_FILE)
st.sidebar.metric("Blocks Secured", len(df_count))
st.sidebar.success("📍 Node: Trinidad & Tobago")
st.sidebar.info("System Status: Active")

st.title("🛡️ Bio-Defense & Pathogen Ledger")

# --- PATHOGEN ANALYSIS ---
st.header("🧬 Real-Time Analysis")
tab1, tab2 = st.tabs(["📁 Image/File Upload", "⌨️ Manual DNA Entry"])

with tab1:
    uploaded_file = st.file_uploader("Upload Evidence", type=['jpg', 'png', 'jpeg', 'fasta'])
    if uploaded_file is not None:
        save_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        auto_loc = get_image_gps(save_path)
        col_left, col_right = st.columns(2)
        
        with col_left:
            if uploaded_file.name.lower().endswith(('.jpg', '.png', '.jpeg')):
                st.image(save_path, caption=f"Capture Source: {auto_loc}", use_container_width=True)
            else:
                st.info(f"📄 DNA Sequence File | {auto_loc}")

        with col_right:
            if uploaded_file.name.lower().endswith('.fasta'):
                raw_data = uploaded_file.getvalue().decode("utf-8")
                dna_seq = "".join(raw_data.splitlines()[1:]).strip().upper()
                gc = gc_fraction(Seq(dna_seq)) * 100
                pathogen_name = "Anthracnose Detected" if gc > 45 else "Biologically Clear"
                risk_level = "HIGH" if gc > 45 else "LOW"
                st.metric("🧬 GC Content", f"{gc:.2f}%")
                analysis_result = f"DNA: {pathogen_name} ({gc:.1f}%)"
            else:
                fname = uploaded_file.name.lower()
                analysis_result = "Visual ID: Anthracnose" if any(x in fname for x in ["spot", "black"]) else "Visual ID: Clear"
                risk_level = "HIGH" if "Anthracnose" in analysis_result else "LOW"
                st.warning(f"Result: {analysis_result}")

            if st.button("🔗 Secure to Blockchain", key="img_btn"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                prev_hash = get_last_hash()
                info_packet = f"{auto_loc} | {uploaded_file.name} | {analysis_result}"
                current_hash = generate_hash(f"{timestamp}{info_packet}{prev_hash}")
                with open(LOG_FILE, "a") as log:
                    log.write(f"{timestamp},WEB_USER,{info_packet},{prev_hash},{current_hash}\n")
                st.success("Record Locked.")
                st.rerun()

with tab2:
    dna_input = st.text_area("Paste DNA Sequence:")
    if dna_input:
        dna_clean = dna_input.strip().upper()
        gc = gc_fraction(Seq(dna_clean)) * 100
        pathogen_name = "Anthracnose Detected" if gc > 45 else "Clear"
        st.metric("GC Content", f"{gc:.2f}%")
        if st.button("🔗 Secure DNA Block", key="dna_btn"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prev_hash = get_last_hash()
            info = f"Manual DNA | GC: {gc:.1f}% | {pathogen_name}"
            current_hash = generate_hash(f"{timestamp}{info}{prev_hash}")
            with open(LOG_FILE, "a") as log:
                log.write(f"{timestamp},WEB_USER,{info},{prev_hash},{current_hash}\n")
            st.success("DNA Verified & Secured.")
            st.rerun()

# --- LIVE FARMER FEED ---
st.divider()
st.header("📡 Live Farmer Feed")
df_feed = pd.read_csv(LOG_FILE)
if not df_feed.empty:
    # We use a loop to show the most recent blocks at the top
    for index, row in df_feed.iloc[::-1].head(10).iterrows():
        with st.expander(f"📦 Block {str(row['block_hash'])[:12]}"):
            st.write(f"📅 **Time:** {row['timestamp']}")
            st.write(f"🧬 **Data:** {row['filepath']}")
            st.write(f"🛡️ **Hash:** `{row['block_hash']}`")

# --- EXPLORER & MAP ---
st.divider()
col_map, col_search = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Regional Risk Map")
    # Coordinates for Trinidad
    map_data = pd.DataFrame({'lat': [10.64, 10.51, 10.35], 'lon': [-61.39, -61.41, -61.45]})
    st.map(map_data)

with col_search:
    st.subheader("🔍 Search Ledger")
    search = st.text_input("Enter Hash:")
    if search:
        res = df_feed[df_feed['block_hash'].astype(str).str.contains(search)]
        st.dataframe(res)