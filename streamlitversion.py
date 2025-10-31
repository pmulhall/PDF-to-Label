# app.py
import fitz  # PyMuPDF
import streamlit as st
import os
from tempfile import TemporaryDirectory

# Screenshot zones for each courier
RECT_COORDS_MAP = {
    "FedEx": (0, 450, 500, 792),
    "DHL": (80, 20, 380, 550)
}

ZOOM = 2.0  # Double resolution

def process_pdf(file_bytes, rect_coords):
    with TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.pdf")
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        doc = fitz.open(input_path)
        image_files = []

        for i, page in enumerate(doc):
            rect = fitz.Rect(*rect_coords)
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
st.title("📦 PDF Screenshot Extractor (FedEx/DHL Selector)")
st.write("Upload a PDF and choose the courier type to extract the relevant screenshot section.")

courier = st.selectbox("Select Courier Type:", ["FedEx", "DHL"])
uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_pdf:
    st.info(f"Processing for **{courier}** layout... please wait.")
    rect_coords = RECT_COORDS_MAP[courier]
    output_data = process_pdf(uploaded_pdf.read(), rect_coords)
    st.success("✅ Done! Click below to download your combined high-resolution screenshots:")
    st.download_button(
        label="📥 Download Processed PDF",
        data=output_data,
        file_name=f"{courier.lower()}_screenshots_combined_highres.pdf",
        mime="application/pdf"
    )
