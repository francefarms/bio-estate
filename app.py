import streamlit as st
import matplotlib.pyplot as plt

# This is a 'lite' version of your analyzer for the web
def calculate_gc(file_content):
    sequence = ""
    # Decode the uploaded file from bytes to text
    lines = file_content.decode("utf-8").splitlines()
    for line in lines:
        if not line.startswith(">"):
            sequence += line.strip()
    
    if not sequence: return 0
    g_count = sequence.upper().count('G')
    c_count = sequence.upper().count('C')
    return (g_count + c_count) / len(sequence) * 100

# --- THE WEB PAGE DESIGN ---
st.title("🥭 Bio-Estate Scanner")
st.write("Upload a DNA sequence to analyze Anthracnose risk.")

uploaded_file = st.file_uploader("Upload .fasta file", type=["fasta"])

if uploaded_file:
    gc_result = calculate_gc(uploaded_file.read())
    st.header(f"GC Content: {gc_result:.2f}%")
    
    # Show the bar chart
    fig, ax = plt.subplots()
    ax.bar(['Mango (Host)', 'Pathogen'], [43.5, gc_result], color=['green', 'red'])
    st.pyplot(fig)