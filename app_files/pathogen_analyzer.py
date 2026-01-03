#!/usr/bin/env python3
import matplotlib.pyplot as plt

def calculate_gc(filename):
    """Reads a FASTA file and calculates the GC percentage."""
    sequence = ""
    try:
        with open(filename, 'r') as file:
            for line in file:
                if not line.startswith(">"):
                    sequence += line.strip()
        if not sequence:
            return 0
        g_count = sequence.upper().count('G')
        c_count = sequence.upper().count('C')
        return (g_count + c_count) / len(sequence) * 100
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None

# --- MAIN ANALYSIS ---
anthracnose_gc = calculate_gc("anthracnose.fasta")
mango_gc = 43.5 

if anthracnose_gc:
    print(f"--- Bio-Estate Pathogen Report ---")
    print(f"Pathogen: Colletotrichum capsici (Anthracnose)")
    print(f"Anthracnose GC Content: {anthracnose_gc:.2f}%")
    print(f"Mango Host GC Content:  {mango_gc:.2f}%")
    print("-" * 34)
    
    print(f"Analysis Complete. Generating Chart...")

    # CREATE THE CHART
    labels = ['Mango (Host)', 'Anthracnose (Pathogen)']
    values = [mango_gc, anthracnose_gc]
    colors = ['#4CAF50', '#FF5722'] 

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=colors)
    plt.ylabel('GC Content (%)')
    plt.title('Genomic Stability Comparison: Mango vs. Anthracnose')
    plt.ylim(0, 100) 

    for i, v in enumerate(values):
        plt.text(i, v + 2, f"{v:.2f}%", ha='center', fontweight='bold')

    # SAVE THE IMAGE
    plt.savefig('gc_comparison.png')
    print("Success! A new file 'gc_comparison.png' has been created in your folder.")