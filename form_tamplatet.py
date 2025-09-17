import streamlit as st
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
import datetime
import subprocess

TEMPLATE_FILE = "Tampalatepr.xlsx"

# === helper tulis aman ke cell merge ===
def safe_write(ws, cell, value):
    """
    Isi cell Excel dengan aman meski ada merge.
    Selalu tulis ke cell kiri-atas merge menggunakan ws.cell(row, col).
    """
    # pecah referensi cell
    col_str = ''.join(filter(str.isalpha, cell))
    row_str = ''.join(filter(str.isdigit, cell))
    col = column_index_from_string(col_str)
    row = int(row_str)

    # cek apakah cell ada di merge
    for rng in ws.merged_cells.ranges:
        if (row, col) in rng.cells:
            row, col = rng.min_row, rng.min_col
            break

    ws.cell(row=row, column=col, value=value)

# === Streamlit App ===
st.title("📑 Form Purchasing Request (PR)")

with st.form("pr_form"):
    st.header("📋 Header PR")
    departemen = st.text_input("Departemen")
    tanggal = st.date_input("Tanggal Pengajuan", value=datetime.date.today())
    jenis_pekerjaan = st.text_input("Jenis Pekerjaan / Unit / Stasiun")
    no_pp = st.text_input("Nomor PP")

    st.header("📦 Detail Barang")
    if "barang" not in st.session_state:
        st.session_state.barang = [
            {"kode": "", "nama": "", "spesifikasi": "", "satuan": "", "qty": 1, "harga": 0, "keterangan": ""}
        ]

    for i, item in enumerate(st.session_state.barang):
        st.subheader(f"Barang {i+1}")
        st.session_state.barang[i]["kode"] = st.text_input(f"Kode Barang {i+1}", value=item["kode"], key=f"kode{i}")
        st.session_state.barang[i]["nama"] = st.text_input(f"Nama Barang {i+1}", value=item["nama"], key=f"nama{i}")
        st.session_state.barang[i]["spesifikasi"] = st.text_area(f"Spesifikasi {i+1}", value=item["spesifikasi"], key=f"spesifikasi{i}")
        st.session_state.barang[i]["satuan"] = st.text_input(f"Satuan {i+1}", value=item["satuan"], key=f"satuan{i}")
        st.session_state.barang[i]["qty"] = st.number_input(f"Kuantitas {i+1}", min_value=1, value=item["qty"], key=f"qty{i}")
        st.session_state.barang[i]["harga"] = st.number_input(f"Estimasi Harga {i+1}", min_value=0, value=item["harga"], key=f"harga{i}")
        st.session_state.barang[i]["keterangan"] = st.text_area(f"Keterangan {i+1}", value=item["keterangan"], key=f"keterangan{i}")
        st.divider()

    tambah_barang = st.form_submit_button("➕ Tambah Barang", type="secondary")

    st.header("💰 Anggaran")
    total_anggaran = st.number_input("Total Anggaran (Rp)", min_value=0, value=0)
    actual_pengeluaran = st.number_input("Actual Pengeluaran (Rp)", min_value=0, value=0)
    permintaan_saat_ini = st.number_input("Permintaan Saat Ini (Rp)", min_value=0, value=0)
    saldo_anggaran = st.number_input("Saldo Anggaran (Rp)", min_value=0, value=0)

    st.header("👨‍💼 Persetujuan")
    diajukan_ktu = st.text_input("Diajukan Oleh (KTU)")
    diajukan_mgr = st.text_input("Diajukan Oleh (Estate Manager)")

    submitted = st.form_submit_button("💾 Simpan & Cetak")

if tambah_barang:
    st.session_state.barang.ap_
