import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path

# Title of the app
st.title('OMAS ARAÇ YAKIT TAKİP SİSTEMİ')

# Display the current data section title
st.subheader('KM VE MAZOT HESAPLAMA')

# List of available Excel files (including the new ones)
files_dict = {
    '06BFD673': '06BFD673.xlsx',
    '01ACB022': '01ACB022.xlsx',
    '01AEE72': '01AEE72.xlsx',
    '01CIN12': '01CIN12.xlsx',
    '01GA546': '01GA546.xlsx',
    '01US433': '01US433.xlsx',
    '01ZD116': '01ZD116.xlsx',
    'FORKLIFT': 'FORKLIFT.xlsx',
    '34BAG417': '34BAG417.xlsx',
    '34BIT882': '34BIT882.xlsx',
    '01BOK56': '01BOK56.xlsx',
    '01SH480': '01SH480.xlsx',
    '01ACJ962': '01ACJ962.xlsx',
    'JENERATOR': 'JENERATOR.xlsx'
}

# Allow the user to select which file to work with
selected_file_key = st.selectbox('Bir plaka seçiniz:', list(files_dict.keys()))
selected_file_name = files_dict[selected_file_key]

# Define the file path for individual vehicle data
current_dir = Path(__file__).parent if '__file__' in locals() else Path.cwd()
EXCEL_FILE = current_dir / selected_file_name

# Define global file for storing global remaining fuel across all vehicles
GLOBAL_FILE = current_dir / 'global_data.xlsx'

# Load or initialize the global fuel data
if GLOBAL_FILE.exists():
    global_df = pd.read_excel(GLOBAL_FILE)
else:
    global_df = pd.DataFrame(columns=['vehicle', 'depodakalanmazot'])

# Function to get global remaining fuel for a specific vehicle
def get_global_remaining_fuel(vehicle_key):
    if vehicle_key in global_df['vehicle'].values:
        return global_df.loc[global_df['vehicle'] == vehicle_key, 'depodakalanmazot'].values[0]
    else:
        return 0

# Display the global "Kalan Mazot" input
global_remaining_fuel = st.number_input('Kalan Mazot (Global):', value=float(get_global_remaining_fuel(selected_file_key)))

# Save the updated global remaining fuel to the global file
if st.button('Update Kalan Mazot'):
    if selected_file_key in global_df['vehicle'].values:
        global_df.loc[global_df['vehicle'] == selected_file_key, 'depodakalanmazot'] = global_remaining_fuel
    else:
        global_df = pd.concat([global_df, pd.DataFrame({'vehicle': [selected_file_key], 'depodakalanmazot': [global_remaining_fuel]})], ignore_index=True)

    global_df.to_excel(GLOBAL_FILE, index=False)
    st.success(f'Global kalan mazot {selected_file_key} için güncellendi!')

# Load the vehicle data or create an empty DataFrame
expected_columns = ['tarih', 'baslangickm', 'mazot', 'katedilenyol', 'toplamyol', 'toplammazot', 'ortalama100', 'kumulatif100', 'depomazot', 'depoyaalinanmazot', 'depodakalanmazot']
if EXCEL_FILE.exists():
    df = pd.read_excel(EXCEL_FILE)
else:
    df = pd.DataFrame(columns=expected_columns)

# Input fields for the user to add new data
tarih = st.text_input('Tarih:')
baslangickm = st.number_input('Mevcut Kilometre:', min_value=0)
mazot = st.number_input('Alınan Mazot:', min_value=0)
depoyaalinanmazot = st.number_input('Depoya Alınan Mazot:', min_value=0)

# When the user clicks the Submit button
if st.button('Ekle'):
    # Calculate katedilenyol (current row's baslangickm - previous row's baslangickm)
    if not df.empty:
        previous_km = df.iloc[-1]['baslangickm']
        katedilenyol = baslangickm - previous_km
        previous_depomazot = df.iloc[-1]['depodakalanmazot']
    else:
        katedilenyol = 0  # No previous entry
        previous_depomazot = 0  # No previous entry for depomazot

    # Calculate toplamyol, ortalama100, kumulatif100, toplammazot
    toplam_yol = df['katedilenyol'].sum() + katedilenyol
    toplammazot = df['mazot'].sum() + mazot
    ortalama100 = (100 / katedilenyol) * mazot if katedilenyol > 0 else 0
    kumulatif100 = (100 / toplam_yol) * mazot if toplam_yol > 0 else 0

    # Use global_remaining_fuel instead of local depomazot
    depomazot = global_remaining_fuel + depoyaalinanmazot - mazot
    depodakalanmazot = depomazot

    # Add the new record
    new_record = {
        'tarih': tarih,
        'baslangickm': baslangickm,
        'mazot': mazot,
        'katedilenyol': katedilenyol,
        'toplamyol': toplam_yol,
        'toplammazot': toplammazot,
        'ortalama100': ortalama100,
        'kumulatif100': kumulatif100,
        'depomazot': depomazot,
        'depoyaalinanmazot': depoyaalinanmazot,
        'depodakalanmazot': depodakalanmazot
    }
    
    # Append the new record to the DataFrame
    df = pd.concat([df, pd.DataFrame(new_record, index=[0])], ignore_index=True)

    # Save the updated DataFrame to the selected Excel file
    df.to_excel(EXCEL_FILE, index=False)
    st.success(f'Data saved to {selected_file_name}!')

    # Update the global depodakalanmazot
    if selected_file_key in global_df['vehicle'].values:
        global_df.loc[global_df['vehicle'] == selected_file_key, 'depodakalanmazot'] = depodakalanmazot
    else:
        global_df = pd.concat([global_df, pd.DataFrame({'vehicle': [selected_file_key], 'depodakalanmazot': [depodakalanmazot]})], ignore_index=True)

    # Save the updated global data
    global_df.to_excel(GLOBAL_FILE, index=False)

# Display the data
st.subheader('Veriler (Depodaki Kalan Mazot, Toplam Mazot, Ortalama 100, ve Kümülatif 100 ile):')
st.dataframe(df[['tarih', 'baslangickm', 'mazot', 'katedilenyol', 'toplamyol', 'toplammazot', 'ortalama100', 'kumulatif100', 'depodakalanmazot']])
