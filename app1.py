import streamlit as st
import torch
from PIL import Image
import fitz  # PyMuPDF for handling PDFs
import os
import tempfile

# Load YOLO model
@st.cache_resource
def load_model():
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov10x_best.pt')
    return model

model = load_model()

# Process single image
def process_image(image):
    results = model(image)
    return results

# Process PDF document
def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages_with_results = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        pix = page.get_pixmap()  # Convert page to an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        results = process_image(img)
        pages_with_results.append((page_number + 1, results))

    return pages_with_results

# Display bounding boxes
def display_results(results, source_type="image"):
    for img_idx, (img, pred) in enumerate(zip(results.imgs, results.pred)):  # Results include predictions
        st.image(img, caption=f"Processed {source_type} {img_idx + 1}")

# Streamlit App UI
st.title("Document Segmentation with YOLO")
st.write("Upload an image or a PDF document to perform segmentation.")

uploaded_file = st.file_uploader("Choose an image or PDF", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    file_type = uploaded_file.type

    if "image" in file_type:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.write("Processing...")
        results = process_image(image)
        display_results(results)

    elif "pdf" in file_type:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.read())
            temp_pdf_path = temp_pdf.name

        st.write("Processing PDF...")
        pdf_results = process_pdf(temp_pdf_path)

        for page_number, results in pdf_results:
            st.write(f"Results for Page {page_number}")
            display_results(results, source_type="PDF page")

        os.remove(temp_pdf_path)

else:
    st.info("Please upload an image or PDF to start.")
