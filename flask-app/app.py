from flask import Flask, redirect, url_for, request, session, render_template, send_file
from keycloak import KeycloakOpenID
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
import requests
import os
import base64
import hashlib
import pymupdf  # PyMuPDF
import json
import jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.writer import PdfFileWriter, copy_into_new_writer
from pyhanko.sign import signers
from pyhanko.sign.fields import append_signature_field, SigFieldSpec
from pyhanko.sign.signers import SimpleSigner
from pyhanko.sign.validation import validate_pdf_signature
from PyPDF2 import PdfReader, PdfWriter

import io 


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
UPLOAD_FOLDER = 'uploads'
SIGNED_FOLDER = 'signed'
SAVED_PDF = os.path.join(UPLOAD_FOLDER, "saved_document.pdf")
SIGNED_PDF = "signed_document.pdf"


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

hostname_flask = os.getenv('HOSTNAME_FLASK')
hostname_kc = os.getenv('HOSTNAME_KC')

KEYCLOAK_SERVER_URL = f'http://{hostname_kc}/'
KEYCLOAK_REALM_NAME = 'master'
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET')
KEYCLOAK_REDIRECT_URI = f'http://{hostname_flask}:8200/callback'
KEYCLOAK_SCOPES = "openid profile email"

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM_NAME,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=False
)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return redirect(keycloak_openid.auth_url(redirect_uri=KEYCLOAK_REDIRECT_URI, scope=KEYCLOAK_SCOPES))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/token"
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': KEYCLOAK_REDIRECT_URI,
        'client_id': KEYCLOAK_CLIENT_ID,
        'client_secret': KEYCLOAK_CLIENT_SECRET,
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(token_url, data=data, headers=headers, verify=False)
    
    if response.status_code == 200:
        token = response.json()
        access_token = token['access_token']
        refresh_token = token['refresh_token']
        
        userinfo_url = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/userinfo"
        userinfo_response = requests.get(userinfo_url, headers={'Authorization': f"Bearer {access_token}"}, verify=False)
        
        if userinfo_response.status_code == 200:
            userinfo = userinfo_response.json()
            session['user'] = userinfo
            session['refresh_token'] = refresh_token
            return redirect(url_for('profile'))
        else:
            return f"Failed to get user info: {userinfo_response.content}"
    else:
        return f"Failed to get token: {response.content}"

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('index'))
    user = session['user']
    return render_template('profile.html', user=user, user_json=user)

import json  # Tambahkan modul json untuk debugging

@app.route('/save_pdf', methods=['POST'])
def save_pdf():
    pdf_file = request.files.get('pdf')

    if not pdf_file:
        return "Tidak ada file yang diunggah!", 400

    if not pdf_file.filename.endswith('.pdf'):
        return "Format file harus PDF!", 400

    save_path = os.path.join(UPLOAD_FOLDER, "saved_document.pdf")
    pdf_file.save(save_path)

    return "PDF berhasil disimpan!", 200

@app.route('/download_signed', methods=['GET'])
def download_signed():
    if not os.path.exists(SIGNED_PDF):
        return "File signed_document.pdf tidak ditemukan.", 400
    return send_file(SIGNED_PDF, as_attachment=True)

@app.route('/tte', methods=['GET', 'POST'])
def tte():
    if 'user' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_id = request.form['id']
        passphrase = request.form['passphrase']

        if not os.path.exists(SAVED_PDF):
            return "File saved_document.pdf tidak ditemukan.", 400

        # Hitung hash SHA-256 dari saved_document.pdf
        with open(SAVED_PDF, 'rb') as f:
            pdf_data = f.read()
            digest_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Kirim hash ke layanan tanda tangan
        headers = {
            "Authorization": "Basic ZXNpZ246d3JqY2dYNjUyNkEyZENZU0FWNnU=",
            "Content-Type": "application/json"
        }
        payload = {
            "nik": "1234567890123456",
            "passphrase": passphrase,
            "signatureProperties": [
                {
                    "tampilan": "INVISIBLE"
                }
            ],
            "file": [
                digest_base64
            ]
        }
        response = requests.post('https://esign-dev.layanan.go.id/api/v2/sign/pdf', json=payload, headers=headers)

        response_data = response.json()
        signature_b64 = response_data.get("file")

        app.logger.info("=== DEBUGGING REQUEST ===")
        app.logger.info(f"Request Headers: {json.dumps(headers, indent=2)}")
        app.logger.info(f"Request Payload: {json.dumps(payload, indent=2)}")
        app.logger.info("=========================")

        app.logger.info("=== DEBUGGING RESPONSE ===")
        app.logger.info(f"Status Code: {response.status_code}")
        app.logger.info(f"Response Body: {json.dumps(signature_b64, indent=2)}")
        app.logger.info("==========================")

        if not signature_b64:
            return "Gagal mendapatkan tanda tangan.", 400

        # Decode dan simpan file hasil tanda tangan
        signed_file_data = base64.b64decode(signature_b64[0])  # Pastikan ini adalah list
        with open(SIGNED_PDF, 'wb') as f:
            f.write(signed_file_data)

        return "File berhasil ditandatangani dan disimpan.", 200

        # if response.status_code == 200:
        #     response_json = response.json()
        #     signature_b64 = response_json.get("signature")

        #     if not signature_b64:
        #         return "Gagal mendapatkan signature dari API.", 400

        #     # Decode tanda tangan digital (signed hash) dari Base64
        #     signature_bytes = base64.b64decode(signature_b64.strip())

        #     # Buat buffer untuk menyimpan PDF sebelum ditandatangani
        #     pdf_buffer = io.BytesIO()

        #     # Buka PDF yang akan ditandatangani
        #     reader = PdfReader(SAVED_PDF)
        #     writer = PdfWriter()

        #     # Salin halaman PDF ke dalam writer
        #     for page in reader.pages:
        #         writer.add_page(page)

        #     # Tambahkan AcroForm jika belum ada
        #     writer._root_object.update({
        #         "/AcroForm": {
        #             "/SigFlags": 3  # Menandakan ada signature di PDF
        #         }
        #     })

        #     # Simpan PDF ke buffer sementara
        #     writer.write(pdf_buffer)
        #     pdf_buffer.seek(0)

        #     # Tambahkan signature field ke dalam PDF
        #     signed_buffer = io.BytesIO()
        #     append_signature_field(pdf_buffer, signed_buffer, sig_field_name="Signature1")

        #     # Buffer untuk hasil akhir PDF yang telah ditandatangani
        #     final_signed_buffer = io.BytesIO()

        #     # Gunakan PyHanko untuk memasukkan signature yang sudah ditandatangani oleh API eksternal
        #     signer = Signer(signature_value=signature_bytes)  # <- Masukkan signed hash di sini
        #     pdf_signer = PdfSigner(signer)

        #     signed_buffer.seek(0)
        #     pdf_signer.sign_pdf(
        #         signed_buffer,
        #         final_signed_buffer,
        #         signature_field_name="Signature1",
        #     )

        #     # Validasi tanda tangan
        #     final_signed_buffer.seek(0)
        #     validation_result = validate_pdf_signature(final_signed_buffer, "Signature1")
        #     if validation_result.intact and validation_result.valid:
        #         final_signed_buffer.seek(0)
        #         return send_file(final_signed_buffer, as_attachment=True, download_name="signed_document.pdf", mimetype="application/pdf")
        #     else:
        #         return "Tanda tangan tidak valid atau tidak utuh.", 400



    return render_template('tte.html')


@app.route('/logout')
def logout():
    refresh_token = session.get('refresh_token')
    if refresh_token:
        logout_url = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/logout"
        data = {
            'client_id': KEYCLOAK_CLIENT_ID,
            'client_secret': KEYCLOAK_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'redirect_uri': f'http://{hostname_flask}:8200/'
        }
        requests.post(logout_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)
        session.clear()
        return redirect(f'http://{hostname_flask}:8200/')
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    app.run(debug=True)
