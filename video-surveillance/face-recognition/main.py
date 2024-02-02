import streamlit as st
from utils.streamlit_utils import handle_files, handle_submit

st.set_page_config(
    page_title="Anonymizer for Video Surveillance", layout="centered"
)

st.title("Anonymizer for Video Surveillance")

st.write(
    """
    This is a demo of the anonymizer for video surveillance.
    """
)

uploaded_files = st.file_uploader(
    "Upload your photo:", accept_multiple_files=True
)

if uploaded_files:
    names = handle_files(uploaded_files)
else:
    names = []

submit = st.button(
    "Submit", on_click=handle_submit
)
