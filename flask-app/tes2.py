import hashlib
import base64
import requests
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import NameObject, DictionaryObject, ArrayObject, TextStringObject, IndirectObject

# Step 1: Generate Digest (Hash) of the PDF
def generate_digest(pdf_path, hash_algorithm="sha256"):
    """Generate a hash digest of the PDF file."""
    hasher = hashlib.new(hash_algorithm)
    with open(pdf_path, "rb") as f:
        while chunk := f.read(4096):  # Read in chunks to handle large files
            hasher.update(chunk)
    return hasher.digest()  # Returns bytes

# Step 2: Send Digest to Remote Signing Service
def get_remote_signature(digest, remote_url, api_key):
    """Send the digest to the remote signing service and get the Base64 PKCS#7 signature."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "hash": base64.b64encode(digest).decode("utf-8"),  # Base64-encoded digest
        "nik": "1234567890123456",  # Hash algorithm used
        "passphrase": "#Bsr3DeVUser.!"
    }
    response = requests.post(remote_url, json=payload, headers=headers)
    print("Request headers:", headers)
    print("Request payload:", payload)
    if response.status_code != 200:
        raise Exception(f"Remote signing failed: {response.text}")
    return response.json()["signature"]  # Base64-encoded PKCS#7 signature

# Step 3: Embed PKCS#7 Signature into PDF
def embed_pkcs7_signature_to_pdf(pdf_path, pkcs7_signature_b64, output_path):
    """Embed the Base64-encoded PKCS#7 signature into the PDF."""
    # Decode the Base64 PKCS#7 signature
    pkcs7_signature = base64.b64decode(pkcs7_signature_b64)

    # Load the PDF
    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()
    writer.appendPagesFromReader(reader)

    # Create a signature field
    sig_field = DictionaryObject()
    sig_field.update({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/FT"): NameObject("/Sig"),  # Field type: Signature
        NameObject("/T"): TextStringObject("Signature1"),  # Name of the signature field
        NameObject("/V"): TextStringObject(pkcs7_signature.decode("latin1")),  # PKCS#7 signature bytes
        NameObject("/Rect"): ArrayObject([
            TextStringObject("50"),  # x1
            TextStringObject("50"),  # y1
            TextStringObject("150"),  # x2
            TextStringObject("100"),  # y2
        ]),
        NameObject("/F"): TextStringObject("4"),  # Flags (4 = Print)
        NameObject("/P"): reader.getPage(0).indirect_ref,  # Reference to the page
    })

    # Add the signature field to the AcroForm dictionary
    if "/AcroForm" not in reader.trailer["/Root"]:
        reader.trailer["/Root"][NameObject("/AcroForm")] = DictionaryObject()
    acro_form = reader.trailer["/Root"]["/AcroForm"]
    if "/Fields" not in acro_form:
        acro_form[NameObject("/Fields")] = ArrayObject()
    acro_form["/Fields"].append(writer._add_object(sig_field))

    # Ensure the AcroForm dictionary has the necessary fields
    acro_form.update({
        NameObject("/SigFlags"): TextStringObject("3"),  # Enable signatures and append-only
    })

    # Save the signed PDF
    with open(output_path, "wb") as f:
        writer.write(f)

# Main Workflow
def main():
    # Paths and configuration
    pdf_path = "document.pdf"  # Input PDF file
    output_path = "signed_document.pdf"  # Output PDF file
    remote_url = "https://api-bsre.bssn.go.id/esign/v2/api/entity/sign/hash-v2"  # Remote signing service URL
    api_key = "eyJ4NXQiOiJOVGRtWmpNNFpEazNOalkwWXpjNU1tWm1PRGd3TVRFM01XWXdOREU1TVdSbFpEZzROemM0WkEiLCJraWQiOiJNell4TW1Ga09HWXdNV0kwWldObU5EY3hOR1l3WW1NNFpUQTNNV0kyTkRBelpHUXpOR00wWkdSbE5qSmtPREZrWkRSaU9URmtNV0ZoTXpVMlpHVmxOZ19SUzI1NiIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJic3JlIiwiYXV0IjoiQVBQTElDQVRJT04iLCJhdWQiOiI1X2FKNmpvRTZlTGJITFRHUElNMG5HOENIQ1FhIiwiYmluZGluZ190eXBlIjoicmVxdWVzdCIsIm5iZiI6MTc0MTQxOTI1NywiYXpwIjoiNV9hSjZqb0U2ZUxiSExUR1BJTTBuRzhDSENRYSIsInNjb3BlIjoiZGVmYXVsdCIsImlzcyI6Imh0dHBzOlwvXC8xMC4yMDEuMjMuODE6OTQ0M1wvb2F1dGgyXC90b2tlbiIsImV4cCI6MTc0MTQyMjg1NywiaWF0IjoxNzQxNDE5MjU3LCJiaW5kaW5nX3JlZiI6ImVkMjc5MWM3N2RhMzhmYzg2ZmU1NzYxODEwYWFlMDhjIiwianRpIjoiY2ZhMTdiZTktMjIwNS00ZDk1LTliMzgtZjM4MGM4NDUwNzMxIn0.t_PJwG1eGp-SFrd_iV5vXEcxlCzu7f10RyRfQbDHRtLTHhCdJ74tg_ee42N7h5wh57YxI2yWgkApH9RT6nWNfsUJ-9fhIuWA4NOU00zjG8DTwed4lU7yv-Vi9hlTnDYg4iDEkPvBShkQo-XSLVO-aYkUVqjDmAWLMyve1GNcu5vFheAS2CmSnc27hhLZ8W6ZFadNW8RFaLrp-IfpSYYfQKLsKgRIO7qFZTCCTKI-0OZHpWaxsdLxfd-RSvSjTfF8yyOL5SxYxEOqEYdNUGA3-NBb_ZsUaxFBmPQ7JV4Tng6ppWnk_YaER71FQCmmhLtZ0T2DKRgMvwpC9htlThCGhQ"  # API key for remote signing service

    # Step 1: Generate digest
    digest = generate_digest(pdf_path)
    print("Digest (SHA-256):", base64.b64encode(digest).decode("utf-8"))

    # Step 2: Get remote signature (PKCS#7)
    signature_b64 = get_remote_signature(digest, remote_url, api_key)
    print("Base64 PKCS#7 Signature:", signature_b64)

    # Step 3: Embed PKCS#7 signature into PDF
    embed_pkcs7_signature_to_pdf(pdf_path, signature_b64, output_path)
    print(f"Signed PDF saved to: {output_path}")

if __name__ == "__main__":
    main()