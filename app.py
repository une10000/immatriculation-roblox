import pandas as pd

# Existing function fetch_immat_data
# ...

# New function to fetch permis data

def fetch_permis_data():
    # Implementation of fetch_permis_data
    pass

# Main code execution starts here

try:
    # Loading df_im
    df_im = fetch_immat_data()
    # Correctly loading df_permis after loading df_im
    df_permis = fetch_permis_data()
except Exception as e:
    print(f"Error fetching data: {e}")

# ... (additional existing code)

# Citizen creation form code
# ...

# Fixing the format for Solde
solde = 15000  # Original
solde_str = f'{solde} $'  # Updated format

# ... (code continuing as originally written)

# Consistency kept for all other parts of the original code