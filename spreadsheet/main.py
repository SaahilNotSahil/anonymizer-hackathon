import streamlit as st

from utils import handle_files, handle_selection, handle_submit

st.set_page_config(
    page_title="Anonymizer for Spreadsheet Data", layout="centered"
)

st.title("Anonymizer Hackathon")
st.write("This is a demo of the anonymizer hackathon project.")

if 'display_modified' not in st.session_state:
    st.session_state.display_modified = False

with st.sidebar:
    uploaded_files = st.file_uploader(
        "Upload a CSV file", type=["csv"], accept_multiple_files=True
    )

if uploaded_files:
    data, file_names, linked_col, linked_tag = handle_files(uploaded_files)
else:
    data, file_names, linked_col, linked_tag = None, None, None, None

if data:
    for d in data:
        key = f"{d[0]}_selectbox"

        if d[1] is True:
            options = ["Remove", "Min-Max", "Binarize"]

            selection = st.selectbox(
                d[0],
                options,
                key=key,
                on_change=handle_selection,
                args=(key,)
            )
        else:
            options = ["Yes", "No"]

            selection = st.selectbox(
                d[0],
                options,
                key=key,
                on_change=handle_selection,
                args=(key,)
            )

submit = st.button(
    "Submit",
    on_click=handle_submit,
    args=(data, file_names, linked_col, linked_tag)
)
