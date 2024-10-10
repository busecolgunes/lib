import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path

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

# Debugging: Check the file path in case of errors
st.write(f"Using file: {EXCEL_FILE}")

# Expected column names
expected_columns = ['tarih', 'baslangickm', 'mazot', 'katedilenyol', 'toplamyol', 'toplammazot', 'ortalama100', 'kumulatif100', 'depomazot', 'depoyaalinanmazot', 'depodakalanmazot']

# Load the data from the file if it exists, otherwise create an empty DataFrame
if EXCEL_FILE.exists():
    df = pd.read_excel(EXCEL_FILE)
else:
    df = pd.DataFrame(columns=expected_columns)

# Display the current data
st.subheader('Veriler:')
st.dataframe(df)

# Create input fields for the user
tarih = st.text_input('Tarih:')
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
    try:
        df.to_excel(EXCEL_FILE, index=False)
        st.success(f'Data saved to {selected_file_name}!')
    except Exception as e:
        st.error(f'Error saving file: {e}')

# File download functionality to get the updated Excel file
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

if not df.empty:
    excel_data = to_excel(df)
    st.download_button(
        label="Excel Dosyasını İndir",
        data=excel_data,
        file_name=selected_file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
