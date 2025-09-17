import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import datetime

TEMPLATE_FILE = "Tamplate PR.pdf.pdf"  # pastikan file template ada di folder

st.title("Form Purchasing Request (PR)")

# =====================
# Bagian PR Header
# =====================
with st.form("pr_form"):
    departemen = st.text_input("Departemen")
    tanggal = st.date_input("Tanggal Pengajuan", value=datetime.date.today())
    jenis_pekerjaan = st.text_input("Jenis Pekerjaan / Unit / Stasiun")
    no_pp = st.text_input("Nomor PP")

    st.subheader("Detail Barang")

    # inisialisasi state
    if "barang" not in st.session_state:
        st.session_state.barang = [
            {"kode": "", "nama": "", "spesifikasi": "", "satuan": "", "qty": 1, "harga": 0, "keterangan": ""}
        ]

    # tampilkan semua barang yang ada di session_state
    for i, item in enumerate(st.session_state.barang):
        st.markdown(f"**Barang {i+1}**")
        st.session_state.barang[i]["kode"] = st.text_input(
            f"Kode Barang {i+1}", value=item["kode"], key=f"kode{i}"
        )
        st.session_state.barang[i]["nama"] = st.text_input(
            f"Nama Barang {i+1}", value=item["nama"], key=f"nama{i}"
        )
        st.session_state.barang[i]["spesifikasi"] = st.text_area(
            f"Spesifikasi {i+1}", value=item["spesifikasi"], key=f"spesifikasi{i}"
        )
        st.session_state.barang[i]["satuan"] = st.text_input(
            f"Satuan {i+1}", value=item["satuan"], key=f"satuan{i}"
        )
        st.session_state.barang[i]["qty"] = st.number_input(
            f"Kuantitas {i+1}", min_value=1, value=item["qty"], key=f"qty{i}"
        )
        st.session_state.barang[i]["harga"] = st.number_input(
            f"Estimasi Harga {i+1}", min_value=0, value=item["harga"], key=f"harga{i}"
        )
        st.session_state.barang[i]["keterangan"] = st.text_area(
            f"Keterangan {i+1}", value=item["keterangan"], key=f"keterangan{i}"
        )
        st.divider()

    tambah_barang = st.form_submit_button("➕ Tambah Barang", type="secondary")
    submitted = st.form_submit_button("💾 Simpan & Cetak")

# tombol tambah barang
if tambah_barang:
    st.session_state.barang.append(
        {"kode": "", "nama": "", "spesifikasi": "", "satuan": "", "qty": 1, "harga": 0, "keterangan": ""}
    )
    st.rerun()

# =====================
# Cetak PDF
# =====================
if submitted:
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 9)

    # --- posisi header (koordinat contoh, perlu disesuaikan dengan template Anda) ---
    can.drawString(120, 770, departemen)
    can.drawString(120, 755, str(tanggal))
    can.drawString(120, 740, jenis_pekerjaan)
    can.drawString(120, 725, no_pp)

    # --- tabel barang ---
    start_y = 680
    row_height = 15
    for i, item in enumerate(st.session_state.barang):
        y = start_y - i * row_height
        total = item["qty"] * item["harga"]
        can.drawString(60, y, item["kode"])
        can.drawString(110, y, item["nama"])
        can.drawString(200, y, item["spesifikasi"])
        can.drawString(350, y, item["satuan"])
        can.drawString(380, y, str(item["qty"]))
        can.drawString(420, y, f"Rp {item['harga']:,}")
        can.drawString(500, y, f"Rp {total:,}")
        can.drawString(560, y, item["keterangan"])

    can.save()
    packet.seek(0)

    # gabung overlay dengan template
    overlay_pdf = PdfReader(packet)
    template_pdf = PdfReader(open(TEMPLATE_FILE, "rb"))
    writer = PdfWriter()

    template_page = template_pdf.pages[0]
    template_page.merge_page(overlay_pdf.pages[0])
    writer.add_page(template_page)

    output_filename = "PR_Output.pdf"
    with open(output_filename, "wb") as f_out:
        writer.write(f_out)

    with open(output_filename, "rb") as f:
        st.download_button("⬇️ Download PR PDF", f, file_name=output_filename)
