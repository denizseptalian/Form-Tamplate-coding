import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import datetime
from pypdf import PdfReader, PdfWriter  # gunakan pypdf (pengganti PyPDF2)

TEMPLATE_FILE = "TamplatePR.pdf.pdf"  # file template PR resmi

st.title("Form Purchasing Request (PR)")

# =====================
# Form Input
# =====================
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
    diajukan_oleh = st.text_input("Diajukan Oleh")
    diperiksa_oleh = st.text_input("Diperiksa Oleh")
    disetujui_oleh = st.text_input("Disetujui Oleh")

    submitted = st.form_submit_button("💾 Simpan & Cetak")

if tambah_barang:
    st.session_state.barang.append(
        {"kode": "", "nama": "", "spesifikasi": "", "satuan": "", "qty": 1, "harga": 0, "keterangan": ""}
    )
    st.rerun()

# =====================
# Cetak ke Template PDF
# =====================
if submitted:
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 9)

    # --- header (koordinat perlu disesuaikan manual sesuai kotak di template) ---
    can.drawString(150, 760, departemen)
    can.drawString(150, 745, str(tanggal))
    can.drawString(150, 730, jenis_pekerjaan)
    can.drawString(150, 715, no_pp)

    # --- detail barang (posisi tabel) ---
    start_y = 670
    row_height = 15
    for i, item in enumerate(st.session_state.barang):
        y = start_y - i * row_height
        total = item["qty"] * item["harga"]
        can.drawString(50, y, item["kode"])
        can.drawString(100, y, item["nama"])
        can.drawString(200, y, item["spesifikasi"])
        can.drawString(350, y, item["satuan"])
        can.drawString(380, y, str(item["qty"]))
        can.drawString(420, y, f"Rp {item['harga']:,}")
        can.drawString(500, y, f"Rp {total:,}")
        can.drawString(560, y, item["keterangan"])

    # --- anggaran ---
    can.drawString(400, 200, f"Rp {total_anggaran:,}")
    can.drawString(400, 185, f"Rp {actual_pengeluaran:,}")
    can.drawString(400, 170, f"Rp {permintaan_saat_ini:,}")
    can.drawString(400, 155, f"Rp {saldo_anggaran:,}")

    # --- persetujuan ---
    can.drawString(150, 120, diajukan_oleh)
    can.drawString(300, 120, diperiksa_oleh)
    can.drawString(450, 120, disetujui_oleh)

    can.save()
    packet.seek(0)

    # Gabungkan overlay dengan template
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
        st.success("✅ PR berhasil dibuat sesuai template resmi!")
        st.download_button("⬇️ Download PR PDF", f, file_name=output_filename)
