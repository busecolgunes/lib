import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
import shutil  # For backup

# Add a title to the app
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

# Define the file path
current_dir = Path(__file__).parent if '__file__' in locals() else Path.cwd()
EXCEL_FILE = current_dir / selected_file_name

# Backup mechanism: create a backup before updating the file
backup_file = EXCEL_FILE.with_suffix('.bak.xlsx')

if EXCEL_FILE.exists():
    shutil.copy(EXCEL_FILE, backup_file)  # Create a backup of the Excel file
    st.info(f'Backup created: {backup_file}')

# Expected column names (now including 'saat')
expected_columns = ['tarih', 'saat', 'baslangickm', 'mazot', 'katedilenyol', 'toplamyol', 'toplammazot', 'ortalama100', 'kumulatif100', 'depomazot', 'depoyaalinanmazot', 'depodakalanmazot']

# Load the data if the file exists, if not, create a new DataFrame with predefined columns
if EXCEL_FILE.exists():
    df = pd.read_excel(EXCEL_FILE)
else:
    df = pd.DataFrame(columns=expected_columns)

# Create input fields for the user
tarih = st.date_input('Tarih:')  # Only date, no time
saat = st.time_input('Saat:')  # Separate time input
baslangickm = st.number_input('Mevcut Kilometre:', min_value=0)
mazot = st.number_input('Alınan Mazot:', min_value=0)
depoyaalinanmazot = st.number_input('Depoya Alınan Mazot:', min_value=0)

# When the user clicks the Submit button
if st.button('Ekle'):
    # Calculate the cumulative mazot (toplammazot)
    toplammazot = df['mazot'].sum() + mazot

    # Calculate katedilenyol (current row's baslangickm - previous row's baslangickm)
    if not df.empty:
        previous_km = df.iloc[-1]['baslangickm']
        katedilenyol = baslangickm - previous_km
        previous_depomazot = df.iloc[-1]['depomazot']
    else:
        katedilenyol = 0  # No previous entry
        previous_depomazot = 0  # No previous entry for depomazot

    # Calculate toplamyol as the sum of all previous katedilenyol plus current
    toplam_yol = df['katedilenyol'].sum() + katedilenyol

    # Calculate ortalama100 and kumulatif100
    if katedilenyol > 0:
        ortalama100 = (100 / katedilenyol) * mazot
    else:
        ortalama100 = 0  # Avoid division by zero

    if toplam_yol > 0:
        kumulatif100 = (100 / toplam_yol) * mazot
    else:
        kumulatif100 = 0  # Avoid division by zero

    # Calculate depomazot and depodakalanmazot
    depomazot = previous_depomazot + depoyaalinanmazot
    depodakalanmazot = depomazot - mazot

    # Add the new record
    new_record = {
        'tarih': tarih.strftime('%Y-%m-%d'),  # Format as string
        'saat': saat.strftime('%H:%M'),  # Format time as string
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

    # Show success message
    st.success(f'Data saved to {selected_file_name}!')

# Continue with the remaining parts of the code...
