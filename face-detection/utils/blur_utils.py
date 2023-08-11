import cv2
import mediapipe as mp

# Initialize the Mediapipe Face Mesh
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh


# Define a function to blur a face region using pixelation

def pixelate_face(image, x, y, w, h, factor=0.1):
    # Crop the face region
    face = image[y:y+h, x:x+w]

    # Resize the face region to a smaller size
    face = cv2.resize(
        face, None, fx=factor, fy=factor, interpolation=cv2.INTER_LINEAR
    )

    # Resize the face region back to the original size
    face = cv2.resize(face, (w, h), interpolation=cv2.INTER_NEAREST)

    # Replace the original image with the pixelated face
    image[y:y+h, x:x+w] = face

    return image


# Define a function to blur a face region using bilateral filter

def bilateral_face(image, x, y, w, h, d=15, sigmaColor=1000, sigmaSpace=1000):
    # Crop the face region
    face = image[y:y+h, x:x+w]

    # Apply bilateral filter to the face region
    face = cv2.bilateralFilter(face, d, sigmaColor, sigmaSpace)

    # Replace the original image with the filtered face
    image[y:y+h, x:x+w] = face

    return image
