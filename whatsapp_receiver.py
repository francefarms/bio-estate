import os
import requests
import hashlib
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

# 1. Initialize the App
app = Flask(__name__)

# --- CONFIGURATION ---
DATA_DIR = "starch_mango_database"
LOG_FILE = "seasonal_log.csv"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- UTILITY FUNCTIONS ---
def generate_hash(data_string):
    return hashlib.sha256(data_string.encode()).hexdigest()

def get_last_hash():
    if not os.path.exists(LOG_FILE):
        return "0000000000000000"
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) > 1:
                return lines[-1].split(",")[-1].strip()
            return "0000000000000000"
    except:
        return "0000000000000000"

def get_analysis_results(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read(500)
            if not content.startswith(">") and not any(base in content.upper() for base in ['A','T','C','G']):
                return "🖼️ Image logged. Visual diagnostics pending."
            
            sequence = "".join([line.strip() for line in content.splitlines() if not line.startswith(">")])
            if not sequence: return "Unknown (Empty)"
            
            gc = (sequence.upper().count('G') + sequence.upper().count('C')) / len(sequence) * 100
            risk = "⚠️ HIGH" if gc > 50 else "✅ LOW"
            return f"{risk} ({gc:.1f}% GC Content)"
    except:
        return "📦 Data secured in ledger."

# --- THE MAIN BOT ROUTE ---
@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    sender_phone = request.values.get('From', 'Unknown').replace('whatsapp:', '')
    num_media = int(request.values.get('NumMedia', 0))
    incoming_msg = request.values.get('Body', '').strip()
    
    resp = MessagingResponse()
    msg = resp.message()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # CASE 1: File Upload (Image or Document)
    if num_media > 0:
        media_url = request.values.get('MediaUrl0')
        content_type = request.values.get('MediaContentType0')
        
        ext = ".jpg" if "image" in content_type else ".fasta"
        filepath = os.path.join(DATA_DIR, f"{sender_phone.replace('+', '')}_{timestamp}{ext}")

        # Save File
        img_data = requests.get(media_url).content
        with open(filepath, 'wb') as f:
            f.write(img_data)

        # Blockchain
        prev_hash = get_last_hash()
        current_hash = generate_hash(f"{timestamp}{sender_phone}{filepath}{prev_hash}")
        
        with open(LOG_FILE, "a") as log:
            log.write(f"{timestamp},{sender_phone},{filepath},{prev_hash},{current_hash}\n")

        analysis = get_analysis_results(filepath)
        msg.body(f"✅ File Secured!\nBlock: {current_hash[:10]}\nResult: {analysis}")

    # CASE 2: Typed DNA Sequence
    elif any(base in incoming_msg.upper() for base in ['A','T','C','G']) and len(incoming_msg) > 5:
        g_count = incoming_msg.upper().count('G')
        c_count = incoming_msg.upper().count('C')
        gc_content = (g_count + c_count) / len(incoming_msg) * 100
        risk = "⚠️ HIGH RISK" if gc_content > 50 else "✅ LOW RISK"
        
        prev_hash = get_last_hash()
        current_hash = generate_hash(f"{timestamp}{sender_phone}{incoming_msg}{prev_hash}")
        
        with open(LOG_FILE, "a") as log:
            log.write(f"{timestamp},{sender_phone},TEXT_DATA,{prev_hash},{current_hash}\n")

        msg.body(f"🧪 DNA Text Analyzed!\nResult: {risk} ({gc_content:.1f}% GC)\nBlock: {current_hash[:10]}")

    else:
        msg.body("Welcome to Bio-Estate. Please send a Mango photo or a DNA sequence to begin.")

    return str(resp)

# 3. Start the server
if __name__ == "__main__":
    app.run(port=5000, debug=True)
