import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import datetime

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

    st.header("📝 Keterangan Tambahan")
    keterangan_umum = st.text_area("Keterangan / Tujuan PR")

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
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 10)

    # Header
    c.drawString(100, 800, f"Departemen: {departemen}")
    c.drawString(100, 785, f"Tanggal Pengajuan: {tanggal}")
    c.drawString(100, 770, f"Jenis Pekerjaan/Unit/Stasiun: {jenis_pekerjaan}")
    c.drawString(100, 755, f"No. PP: {no_pp}")

    # Detail Barang
    y = 730
    c.drawString(100, y, "Detail Barang:")
    y -= 15
    for item in st.session_state.barang:
        total = item["qty"] * item["harga"]
        c.drawString(110, y, f"{item['kode']} | {item['nama']} | {item['spesifikasi']} | "
                             f"{item['satuan']} | {item['qty']} | Rp{item['harga']:,} | Rp{total:,} | {item['keterangan']}")
        y -= 15

    # Anggaran
    y -= 20
    c.drawString(100, y, f"Total Anggaran: Rp{total_anggaran:,}")
    y -= 15
    c.drawString(100, y, f"Actual Pengeluaran: Rp{actual_pengeluaran:,}")
    y -= 15
    c.drawString(100, y, f"Permintaan Saat Ini: Rp{permintaan_saat_ini:,}")
    y -= 15
    c.drawString(100, y, f"Saldo Anggaran: Rp{saldo_anggaran:,}")

    # Keterangan
    y -= 25
    c.drawString(100, y, f"Keterangan: {keterangan_umum}")

    # Persetujuan
    y -= 40
    c.drawString(100, y, f"Diajukan Oleh: {diajukan_oleh}")
    y -= 15
    c.drawString(100, y, f"Diperiksa Oleh: {diperiksa_oleh}")
    y -= 15
    c.drawString(100, y, f"Disetujui Oleh: {disetujui_oleh}")

    c.showPage()
    c.save()

    buffer.seek(0)
    st.download_button("⬇️ Download PR PDF", data=buffer, file_name="PR_Output.pdf", mime="application/pdf")
