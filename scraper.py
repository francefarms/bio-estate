import requests
import json

def get_prices():
    # Example using a free endpoint (replace with your Commodities-API key later)
    # For now, we simulate the data structure your website expects
    url = "https://api.exchangerate-api.com/v4/latest/USD" 
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # We create a specific commodities file
        # In a real setup, you'd map these to Cocoa, Coffee, etc.
        output = {
            "rates": {
                "Cocoa (Ton)": 9450.00, # You can scrape these from FocusEconomics
                "Coffee (lb)": 2.45,
                "Sugar (lb)": 0.22,
                "Mango (Crate)": 15.00 
            },
            "last_updated": data["date"]
        }
        
        with open('commodities.json', 'w') as f:
            json.dump(output, f)
            
        print("Prices updated successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_prices()