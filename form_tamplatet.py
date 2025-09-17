import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import datetime

# coba impor pypdf dulu, fallback ke PyPDF2
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    from PyPDF2 import PdfReader, PdfWriter

TEMPLATE_FILE = "TamplatePR.pdf.pdf"  # template PR resmi

# =====================
# Koordinat Requirement Text
# =====================
coords = {
    "header": {
        "departemen": (150, 770),
        "tanggal": (400, 770),
        "jenis_pekerjaan": (150, 755),
        "no_pp": (400, 755),
    },
    "barang": {
        "kode": 40,
        "nama": 100,
        "spesifikasi": 200,
        "satuan": 350,
        "qty": 390,
        "harga": 430,
        "total": 500,
        "keterangan": 560,
        "start_y": 700,
        "row_height": 15,
    },
    "anggaran": {
        "total": (400, 200),
        "actual": (400, 185),
        "permintaan": (400, 170),
        "saldo": (400, 155),
    },
    "persetujuan": {
        "diajukan": (120, 120),
        "diperiksa": (300, 120),
        "disetujui": (480, 120),
    }
}

# =====================
# Streamlit Form
# =====================
st.title("Form Purchasing Request (PR)")

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
# Generate PDF
# =====================
if submitted:
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 9)

    # --- header ---
    can.drawString(*coords["header"]["departemen"], departemen)
    can.drawString(*coords["header"]["tanggal"], str(tanggal))
    can.drawString(*coords["header"]["jenis_pekerjaan"], jenis_pekerjaan)
    can.drawString(*coords["header"]["no_pp"], no_pp)

    # --- detail barang ---
    start_y = coords["barang"]["start_y"]
    row_h = coords["barang"]["row_height"]
    for i, item in enumerate(st.session_state.barang):
        y = start_y - i * row_h
        total = item["qty"] * item["harga"]
        can.drawString(coords["barang"]["kode"], y, item["kode"])
        can.drawString(coords["barang"]["nama"], y, item["nama"])
        can.drawString(coords["barang"]["spesifikasi"], y, item["spesifikasi"])
        can.drawString(coords["barang"]["satuan"], y, item["satuan"])
        can.drawString(coords["barang"]["qty"], y, str(item["qty"]))
        can.drawString(coords["barang"]["harga"], y, f"Rp {item['harga']:,}")
        can.drawString(coords["barang"]["total"], y, f"Rp {total:,}")
        can.drawString(coords["barang"]["keterangan"], y, item["keterangan"])

    # --- anggaran ---
    can.drawString(*coords["anggaran"]["total"], f"Rp {total_anggaran:,}")
    can.drawString(*coords["anggaran"]["actual"], f"Rp {actual_pengeluaran:,}")
    can.drawString(*coords["anggaran"]["permintaan"], f"Rp {permintaan_saat_ini:,}")
    can.drawString(*coords["anggaran"]["saldo"], f"Rp {saldo_anggaran:,}")

    # --- persetujuan ---
    can.drawString(*coords["persetujuan"]["diajukan"], diajukan_oleh)
    can.drawString(*coords["persetujuan"]["diperiksa"], diperiksa_oleh)
    can.drawString(*coords["persetujuan"]["disetujui"], disetujui_oleh)

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
        st.success("✅ PR berhasil dibuat sesuai template!")
        st.download_button("⬇️ Download PR PDF", f, file_name=output_filename)
