import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path

# Add a title to the app
st.title('OMAS ARAÇ YAKIT TAKİP SİSTEMİ')

# Define the file path for global fuel data
current_dir = Path(__file__).parent if '__file__' in locals() else Path.cwd()
GLOBAL_FILE = current_dir / 'global_fuel_data.xlsx'

# Load or initialize the global fuel data
if GLOBAL_FILE.exists():
    global_fuel_df = pd.read_excel(GLOBAL_FILE)  # Load the file if it exists
else:
    global_fuel_df = pd.DataFrame({'depodakalanmazot': [0]})  # Initialize with default value of 0 if no file

# Get the current global remaining fuel value
global_remaining_fuel = global_fuel_df['depodakalanmazot'].iloc[0]

# Create a number input for the global "Kalan Mazot" above everything
new_global_remaining_fuel = st.number_input('Kalan Mazot (Global):', value=float(global_remaining_fuel))

# Button to update the global remaining fuel value
if st.button('Kalan Mazot Güncelle'):
    # Update the value in the DataFrame
    global_fuel_df['depodakalanmazot'].iloc[0] = new_global_remaining_fuel
    
    # Save the updated value to the global Excel file
    global_fuel_df.to_excel(GLOBAL_FILE, index=False)
    
    st.success('Global kalan mazot güncellendi!')

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

# Define the file path for the selected Excel file
EXCEL_FILE = current_dir / selected_file_name

# Load the data from the file if it exists, otherwise create an empty DataFrame
expected_columns = ['tarih', 'baslangickm', 'mazot', 'katedilenyol', 'toplamyol', 'toplammazot', 'ortalama100', 'kumulatif100', 'depomazot', 'depoyaalinanmazot', 'depodakalanmazot']

if EXCEL_FILE.exists():
    df = pd.read_excel(EXCEL_FILE)
else:
    df = pd.DataFrame(columns=expected_columns)

# Create input fields for the user to input data
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

    # Calculate the cumulative mazot (toplammazot) across all rows
    toplammazot = df['mazot'].sum() + mazot

    # Calculate depomazot and depodakalanmazot
    depomazot = previous_depomazot + depoyaalinanmazot - mazot
    depodakalanmazot = depomazot  # Depodaki kalan mazot

    # Add the new record
    new_record = {
        'tarih': tarih,
        'baslangickm': baslangickm,
        'mazot': mazot,
        'katedilenyol': katedilenyol,
        'toplamyol': toplam_yol,
        'toplammazot': toplammazot,  # Add toplammazot to the record
        'ortalama100': ortalama100,  # Add ortalama100 to the record
        'kumulatif100': kumulatif100,  # Add kumulatif100 to the record
        'depomazot': depomazot,
        'depoyaalinanmazot': depoyaalinanmazot,
        'depodakalanmazot': depodakalanmazot
    }

    # Append the new record to the DataFrame
    df = pd.concat([df, pd.DataFrame(new_record, index=[0])], ignore_index=True)

    # Save the updated DataFrame to the selected Excel file
    df.to_excel(EXCEL_FILE, index=False)
    st.success(f'Data saved to {selected_file_name}!')

# Move the data table to the bottom of the app
st.subheader('Veriler:')
st.dataframe(df)

# --- Upload Excel file and append to existing data ---
uploaded_file = st.file_uploader("Bir Excel dosyası yükleyin ve mevcut veriye ekleyin", type="xlsx")
if uploaded_file is not None:
    try:
        # Read the uploaded Excel file
        uploaded_df = pd.read_excel(uploaded_file)
        
        # Standardize column names (lowercase and strip whitespaces) for both the uploaded file and the expected columns
        uploaded_df.columns = uploaded_df.columns.str.lower().str.strip()  # Normalize uploaded columns
        expected_columns_normalized = [col.lower().strip() for col in expected_columns]  # Normalize expected columns

        # Compare columns between uploaded file and expected columns
        uploaded_columns = list(uploaded_df.columns)
        missing_columns = [col for col in expected_columns_normalized if col not in uploaded_columns]
        extra_columns = [col for col in uploaded_columns if col not in expected_columns_normalized]

        if not missing_columns and not extra_columns:
            # Rename columns in the uploaded file to match exactly with expected columns
            uploaded_df.columns = expected_columns  # This ensures the correct naming

            # Append the uploaded data to the existing data
            df = pd.concat([df, uploaded_df], ignore_index=True)

            # Save the updated DataFrame to the selected Excel file
            df.to_excel(EXCEL_FILE, index=False)

            st.success(f'{uploaded_file.name} verileri {selected_file_name} dosyasına eklendi!')
        else:
            st.error('Yüklenen dosya sütunları uyuşmuyor!')
            if missing_columns:
                st.warning(f"Beklenen ancak eksik olan sütunlar: {', '.join(missing_columns)}")
            if extra_columns:
                st.warning(f"Fazla olan sütunlar: {', '.join(extra_columns)}")
    except Exception as e:
        st.error(f'Hata oluştu: {e}')

# --- Row deletion functionality ---
st.subheader('Veri Silme Seçenekleri')

# Row deletion
if st.checkbox('Veri Satırı Sil'):
    if not df.empty:
        # Display the data as a table with an index
        st.write("Lütfen silinecek satırın numarasını seçin:")
        st.dataframe(df)

        # User input to select the row index to delete
        row_index_to_delete = st.number_input('Silinecek satır numarası:', min_value=0, max_value=len(df) - 1, step=1)

        # Confirm and delete the selected row
        if st.button('Satırı Sil'):
            df = df.drop(df.index[row_index_to_delete])  # Drop the row at the given index
            df.to_excel(EXCEL_FILE, index=False)  # Save the updated DataFrame to Excel file
            st.success(f"Satır {row_index_to_delete} başarıyla silindi!")
    else:
        st.warning("Silinecek veri yok.")
