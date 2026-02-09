import pandas as pd

# Load data from the "Points Permis" worksheet
df_permis = pd.read_excel('path_to_your_excel_file.xlsx', sheet_name='Points Permis')

def fetch_permis_data():
    # Example function to fetch permis data
    permis_info = df_permis.loc[df_permis['some_column'] == 'some_value']
    # Format the Solde field
    permis_info['Solde'] = permis_info['Solde'].apply(lambda x: f'{x:,.0f} $')
    return permis_info

# Example usage
# permis_data = fetch_permis_data()