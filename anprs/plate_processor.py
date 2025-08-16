import cv2
import numpy as np
import pytesseract
from PIL import Image


class PlateProcessor:
    def __init__(self):
        # Initialize cascade classifier for license plate detection
        self.plate_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_russian_plate_number.xml"
        )

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        return blur

    def detect_plate(self, image):
        preprocessed = self.preprocess_image(image)
        plates = self.plate_cascade.detectMultiScale(
            preprocessed, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        if len(plates) == 0:
            return None

        # Return the first detected plate
        x, y, w, h = plates[0]
        plate_img = image[y : y + h, x : x + w]
        return plate_img

    def extract_text(self, plate_image):
        # Additional preprocessing for OCR
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # OCR
        text = pytesseract.image_to_string(thresh, config="--psm 7")
        # Clean the text
        cleaned_text = "".join(c for c in text if c.isalnum())
        return cleaned_text.upper()
