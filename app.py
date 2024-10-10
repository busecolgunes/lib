import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
import shutil  # For backup
from datetime import datetime
import locale

# Set locale to Turkish for date formatting
locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")

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
tarih = st.date_input('Tarih:', value=datetime.now())  # Only date, no time
saat = st.text_input('Saat (HH:MM formatında giriniz):')  # Manual time input (as text)

# Validate the time format
try:
    saat_dt = datetime.strptime(saat, '%H:%M') if saat else None
except ValueError:
    st.error("Lütfen saati HH:MM formatında giriniz!")

# Input fields for other data
baslangickm = st.number_input('Mevcut Kilometre:', min_value=0)
mazot = st.number_input('Alınan Mazot:', min_value=0)
depoyaalinanmazot = st.number_input('Depoya Alınan Mazot:', min_value=0)

# When the user clicks the Submit button
if st.button('Ekle'):
    if not saat_dt:
        st.error("Lütfen geçerli bir saat giriniz.")
    else:
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
            'tarih': tarih,  # Store the raw date input
            'saat': saat,  # User-entered time
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

# File upload functionality to append data
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

# Delete functionality
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
        if st.button('Delete Row'):
            df = df.drop(df.index[row_index_to_delete]).reset_index(drop=True)

            # Save the updated DataFrame to the selected Excel file
            df.to_excel(EXCEL_FILE, index=False)

            st.success(f'Row {row_index_to_delete} deleted from {selected_file_name}!')
    else:
        st.warning('No data available to delete.')

# Excel file download link
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

if st.button('Excel Dosyasını İndir'):
    excel_data = to_excel(df)
    st.download_button(
        label='Download Excel File',
        data=excel_data,
        file_name=selected_file_name,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Excel file deletion
if st.checkbox('Yüklenen Excel Dosyasını Sil'):
    if EXCEL_FILE.exists():
        if st.button('Excel Dosyasını Sil'):
            EXCEL_FILE.unlink()  # Delete the Excel file
            st.success(f'{selected_file_name} başarıyla silindi!')
    else:
        st.warning('Bu dosya zaten mevcut değil.')

# Display the updated data under "KM VE MAZOT HESAP"
st.subheader('Veriler:')
st.dataframe(df)  # Show the latest state of the DataFrame at the end
