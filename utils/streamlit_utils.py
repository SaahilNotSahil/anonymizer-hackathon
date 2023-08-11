import cv2
import streamlit as st


@st.cache_resource
def get_cam():
    cap = cv2.VideoCapture(0)

    return cap
