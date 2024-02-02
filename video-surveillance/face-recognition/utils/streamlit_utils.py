import os

import cv2
import face_recognition
import streamlit as st


@st.cache_resource
def get_cam():
    cap = cv2.VideoCapture(0)

    return cap


@st.cache_data
def handle_files(files):
    file_names = []

    for file in files:
        file_name = file.name.strip().replace(" ", "_").split(".")[0]
        file.seek(0)

        faces_folder = "faces"

        if file:
            with open(f"{faces_folder}/{file_name}.jpg", "wb") as f:
                f.write(file.read())

        file_names.append(file_name)

    return file_names


def handle_submit():
    FRAME_WINDOW = st.image([])

    cap = get_cam()

    known_faces = []
    known_names = []

    faces_folder = "faces"

    for filename in os.listdir(faces_folder):
        if filename.endswith(".jpg") or \
                filename.endswith(".png") or filename.endswith(".jpeg"):
            image = face_recognition.load_image_file(
                os.path.join(faces_folder, filename)
            )
            face_encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(face_encoding)
            known_names.append(os.path.splitext(filename)[0])

    print(known_names)

    quit = st.button(
        "Quit",
        key="tab6"
    )

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        frame = cv2.flip(frame, 1)

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings
        ):
            name = "Unknown"

            matches = face_recognition.compare_faces(
                known_faces, face_encoding)
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

            if name != "Unknown":
                face_image = frame[top:bottom, left:right]
                blurred_face = cv2.GaussianBlur(face_image, (99, 99), 30)
                frame[top:bottom, left:right] = blurred_face

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_DUPLEX,
                0.5,
                (0, 255, 0),
                1
            )

        FRAME_WINDOW.image(frame)

        if quit:
            break
