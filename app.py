import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Function to fetch permis data
def fetch_permis_data(citizen_id):
    try:
        response = requests.get(f"http://example.com/api/permits/{citizen_id}")
        response.raise_for_status()
        return response.json()  # Assuming the API returns JSON data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for citizen {citizen_id}: {e}")
        return None

# Proper formatting function for Solde
def format_solde(solde):
    try:
        return "{:,.2f}".format(float(solde))  # Format as a float with 2 decimal places
    except ValueError:
        print(f"Invalid value for Solde: {solde}")
        return "Invalid"

# Example route to create citizen
@app.route('/create_citizen', methods=['POST'])
def create_citizen():
    data = request.get_json()
    citizen_id = data.get('citizen_id')
    
    permis_data = fetch_permis_data(citizen_id)
    if permis_data is None:
        return jsonify({"error": "Data not found"}), 404

    # Assume further processing occurs here
    solde = format_solde(permis_data.get('solde', 0))
    
    return jsonify({"message": "Citizen created successfully", "solde": solde}), 201

if __name__ == '__main__':
    app.run(debug=True)