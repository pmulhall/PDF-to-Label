# app.py
import fitz  # PyMuPDF
import streamlit as st
import os
from tempfile import TemporaryDirectory

RECT_COORDS = (0, 450, 500, 792)
ZOOM = 2.0  # Double resolution

def process_pdf(file_bytes):
    with TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.pdf")
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        doc = fitz.open(input_path)
        image_files = []

        for i, page in enumerate(doc):
            rect = fitz.Rect(*RECT_COORDS)
            matrix = fitz.Matrix(ZOOM, ZOOM)
            pix = page.get_pixmap(matrix=matrix, clip=rect)
            image_path = os.path.join(tmpdir, f"screenshot_page_{i+1}.png")
            pix.save(image_path)
            image_files.append(image_path)

        doc.close()

        output_pdf = fitz.open()
        for image_path in image_files:
            img_doc = fitz.open(image_path)
            pdfbytes = img_doc.convert_to_pdf()
            img_pdf = fitz.open("pdf", pdfbytes)
            output_pdf.insert_pdf(img_pdf)
            img_doc.close()

        output_path = os.path.join(tmpdir, "screenshots_combined_highres.pdf")
        output_pdf.save(output_path)
        output_pdf.close()

        with open(output_path, "rb") as f:
            return f.read()

# Streamlit UI
st.title("📸 PDF Screenshot Extractor (Web Version)")
uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_pdf:
    st.info("Processing your file, please wait...")
    output_data = process_pdf(uploaded_pdf.read())
    st.success("Done! Click below to download the combined high-resolution screenshots:")
    st.download_button("📥 Download PDF", output_data, file_name="screenshots_combined_highres.pdf")
