import hashlib
import requests
import base64
from pikepdf import Pdf, Name, String

# Konfigurasi API eksternal
API_URL = "https://api-bsre.bssn.go.id/esign/v2/api/entity/sign/hash-v2"
API_KEY = "eyJ4NXQiOiJOVGRtWmpNNFpEazNOalkwWXpjNU1tWm1PRGd3TVRFM01XWXdOREU1TVdSbFpEZzROemM0WkEiLCJraWQiOiJNell4TW1Ga09HWXdNV0kwWldObU5EY3hOR1l3WW1NNFpUQTNNV0kyTkRBelpHUXpOR00wWkdSbE5qSmtPREZrWkRSaU9URmtNV0ZoTXpVMlpHVmxOZ19SUzI1NiIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJic3JlIiwiYXV0IjoiQVBQTElDQVRJT04iLCJhdWQiOiI1X2FKNmpvRTZlTGJITFRHUElNMG5HOENIQ1FhIiwiYmluZGluZ190eXBlIjoicmVxdWVzdCIsIm5iZiI6MTc0MTM4NzQ2MywiYXpwIjoiNV9hSjZqb0U2ZUxiSExUR1BJTTBuRzhDSENRYSIsInNjb3BlIjoiZGVmYXVsdCIsImlzcyI6Imh0dHBzOlwvXC8xMC4yMDEuMjMuODE6OTQ0M1wvb2F1dGgyXC90b2tlbiIsImV4cCI6MTc0MTM5MTA2MywiaWF0IjoxNzQxMzg3NDYzLCJiaW5kaW5nX3JlZiI6ImJjYzNmNjlmZmRmNDQ2YjY3MDU4YjkxM2JhZjI4ZmFjIiwianRpIjoiY2IxNWUxMTUtZWY2MS00MGQ4LTljZjgtNjBmNGU4OTQ4YjJjIn0.Q2ZsF3s8VRtiPnFTVp0oWCAlR2ECWVz8oNzqzqTvw4mkOJkSUmthv92ImqH2x16HQi8dFykikiqPwbL9zW-e2zRckjgMdQrF67tdcwwoYH9cTRHv3LissQg0t5ZLQOClHZ421sm48QS4IwQ_4iujVU9e0L8qcL_Xdz-cPKs7pahf5jOc2mtfvcuLv9CvGLRdD47FzUM5fViwKTUqQqc3NJ2w6mkmqPz1eTmRH7Dbsr9QHYh1byPtJwB8tffmT9x3v787KSY3ML1I0TQ3zIu1YUCOvZ0QXYbNy67THOiH3LVjK_KzlwafIHkrrge6V52vXSRiOdi4IUWjbCTfuNmPyw"  # Ganti dengan API Key yang valid

def generate_pdf_digest(pdf_path):
    """Menghitung hash SHA-256 dari PDF."""
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    digest = base64.b64encode(hashlib.sha256(pdf_data).digest()).decode('utf-8')
    return digest

def get_signature_from_api(digest):
    """Mengirim digest ke API eksternal dan mendapatkan signature."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {"hash": digest, "nik": "1234567890123456", "passphrase": "#Bsr3DeVUser.!"}

    response = requests.post(API_URL, json=data, headers=headers)

    if response.status_code == 200:
        return response.json().get("signature")
    else:
        print("Error:", response.text)
        return None

def insert_signature_to_pdf(pdf_path, signed_pdf_path, signature):
    """Menyisipkan signature ke PDF."""
    pdf = Pdf.open(pdf_path)
    sig_page = pdf.pages[0]  # Pilih halaman pertama

    # Tambahkan annotation untuk tanda tangan digital
    sig_annot = sig_page.add_annotation({
        "Subtype": Name("/Widget"),
        "FT": Name("/Sig"),
        "T": String("Signature1"),
        "Rect": [100, 100, 300, 150],  # Posisi tanda tangan di halaman
        "Contents": String(signature),  # Simpan signature di dalam field
    })

    pdf.save(signed_pdf_path)
    print(f"✅ PDF Signed: {signed_pdf_path}")

def main():
    input_pdf = "document.pdf"
    output_pdf = "signed_document.pdf"

    # 1️⃣ Generate Digest PDF
    digest = generate_pdf_digest(input_pdf)
    print(f"🔹 PDF Digest: {digest}")

    # 2️⃣ Kirim ke API eksternal untuk mendapatkan signature
    signature = get_signature_from_api(digest)
    if not signature:
        print("❌ Gagal mendapatkan signature dari API.")
        return

    print(f"🔹 Signature Received: {signature[:50]}...")  # Tampilkan sebagian signature

    # 3️⃣ Sisipkan Signature ke PDF
    insert_signature_to_pdf(input_pdf, output_pdf, signature)

if __name__ == "__main__":
    main()
