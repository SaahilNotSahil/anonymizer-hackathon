import cv2
import streamlit as st

from utils import bilateral_face, mp_drawing, mp_face_mesh, pixelate_face

st.set_page_config(
    page_title="Anonymizer for Video Surveillance", layout="centered"
)

st.title("Anonymizer for Video Surveillance")

st.write(
    """
    This is a demo of the anonymizer for video surveillance.
    """
)

FRAME_WINDOW = st.image([])

cap = cv2.VideoCapture(1)

blur_mode = st.selectbox(
    'Select blur mode:',
    ('gaussian', 'pixelate', 'bilateral', 'none'),
    on_change=cap.release
)

draw_landmark = st.button('Draw landmark', on_click=cap.release)
hide_landmark = st.button('hide landmark', on_click=cap.release)
quit = st.button("Quit", on_click=cap.release)

with mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Convert the image to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image with the Face Mesh model
        results = face_mesh.process(rgb)

        # Draw the face landmarks and blur the faces on the image
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                if draw_landmark:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=mp_drawing.DrawingSpec(
                            color=(255, 255, 0), thickness=1, circle_radius=1
                        ),
                        connection_drawing_spec=mp_drawing.DrawingSpec(
                            color=(0, 255, 255), thickness=1
                        )
                    )
                else:
                    pass

                # Get the bounding box coordinates of the face from the landmarks
                x = int(
                    min([landmark.x for landmark in face_landmarks.landmark]) * frame.shape[1])
                y = int(
                    min([landmark.y for landmark in face_landmarks.landmark]) * frame.shape[0])
                w = int((max([landmark.x for landmark in face_landmarks.landmark]) - min(
                    [landmark.x for landmark in face_landmarks.landmark])) * frame.shape[1])
                h = int((max([landmark.y for landmark in face_landmarks.landmark]) - min(
                    [landmark.y for landmark in face_landmarks.landmark])) * frame.shape[0])

                # Blur the face according to the current blur mode
                if blur_mode == "gaussian":
                    frame[y:y+h, x:x+w] = cv2.GaussianBlur(
                        frame[y:y+h, x:x+w], (99, 99), 0
                    )
                elif blur_mode == "pixelate":
                    frame = pixelate_face(frame, x, y, w, h)
                elif blur_mode == "bilateral":
                    frame = bilateral_face(frame, x, y, w, h)
                elif blur_mode == "none":
                    pass

            # Display the number of faces detected on the image
            cv2.putText(
                frame,
                f"Faces: {len(results.multi_face_landmarks)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
        else:
            # Display a message if no faces are detected on the image
            cv2.putText(
                frame,
                "No faces detected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        # Display the current blur mode on the image
        cv2.putText(
            frame,
            f"Blur mode: {blur_mode}",
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        FRAME_WINDOW.image(frame)

        if hide_landmark:
            draw_landmark = False
        elif quit:
            break

cap.release()
