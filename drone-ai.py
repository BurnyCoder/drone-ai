import cv2
import time
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
from ultralytics import YOLO
import glob # Added for finding image files

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Testing Mode Configuration
TESTING_MODE_STR = os.getenv("TESTING_MODE", "false") # Default to false if not set
TEST_IMAGE_DIR = os.getenv("TEST_IMAGE_DIR", "test_images") # Directory containing test images
# RTMP URL Configuration
RTMP_URL = os.getenv("RTMP_URL", "rtmp://192.168.158.143/live/key")
# Make sure to set the OPENAI_API_KEY environment variable
# You can get one from https://platform.openai.com/account/api-keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# What do you want to ask the AI about the image?
OPENAI_PROMPT = os.getenv("OPENAI_PROMPT", "What is in this image?") # Default prompt if not set
# How often to capture and send frame (in seconds)
CAPTURE_INTERVAL_STR = os.getenv("CAPTURE_INTERVAL", "5") # Default interval if not set

TESTING_MODE = TESTING_MODE_STR.lower() == 'true'

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.")
    exit()

# Define CAPTURE_INTERVAL before it might be used
try:
    CAPTURE_INTERVAL = float(CAPTURE_INTERVAL_STR)
except ValueError:
    print(f"Error: Invalid value for CAPTURE_INTERVAL environment variable: '{CAPTURE_INTERVAL_STR}'. Must be a number.")
    exit()

if TESTING_MODE:
    if not TEST_IMAGE_DIR:
        print("Error: TESTING_MODE is enabled, but TEST_IMAGE_DIR environment variable is not set.")
        exit()
    if not os.path.isdir(TEST_IMAGE_DIR):
        print(f"Error: TEST_IMAGE_DIR '{TEST_IMAGE_DIR}' is not a valid directory.")
        exit()
    print(f"--- TESTING MODE ENABLED ---")
    print(f"Reading images from: {TEST_IMAGE_DIR}")
    print(f"Processing interval: {CAPTURE_INTERVAL} seconds")
elif not RTMP_URL: # Only check RTMP_URL if not in testing mode
    print("Error: RTMP_URL environment variable not set (and TESTING_MODE is false).")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY)

# --- YOLO Setup ---
# Load a pretrained YOLO11n model globally to avoid reloading on each call
yolo_model = YOLO("yolo11n.pt")

def encode_image_to_base64(frame):
    """Encodes a numpy array image to a base64 string."""
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

def analyze_image_with_openai(base64_image):
    """Sends the image to OpenAI Vision API and returns the description."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Or use the latest vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": OPENAI_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        # Extract the content from the response
        if response.choices:
            return response.choices[0].message.content
        else:
            return "No description returned from API."
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def analyze_image_with_yolo(frame):
    """Analyzes an image frame using YOLO and prints results."""
    print("Analyzing frame with YOLO...")
    try:
        # Perform object detection on the frame
        # The frame is already a numpy array, which YOLO can handle directly
        results = yolo_model(frame) 

        # Process and print results (or return them)
        if results:
            # results[0].show() # This would open a window, might not be ideal for server/RTMP context
            print("\n--- YOLO Detection Results ---")
            # Print basic info about detections
            results[0].show()
            # You could iterate through results[0].boxes, results[0].masks, etc. 
            # to get specific details like bounding boxes, classes, confidences.
            print("----------------------------\n")
            # For now, just returning the results object
            return results
        else:
            print("No objects detected by YOLO.")
            return None
    except Exception as e:
        print(f"Error during YOLO analysis: {e}")
        return None

def process_frame(frame):
    """Processes a single frame with YOLO and OpenAI."""
    print(f"Processing frame at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # --- YOLO Analysis ---
    analyze_image_with_yolo(frame) # Call YOLO analysis

    # --- OpenAI Analysis ---
    # Encode image for OpenAI
    base64_image = encode_image_to_base64(frame)

    # Analyze image
    print("Sending frame to OpenAI for analysis...")
    description = analyze_image_with_openai(base64_image)

    if description:
        print("\n--- OpenAI Analysis Result ---")
        print(description)
        print("-----------------------------\n")
    else:
        print("No description received from OpenAI.") # Added for clarity

def run_rtmp_mode():
    """Runs the script in RTMP stream mode."""
    print(f"Connecting to RTMP stream: {RTMP_URL}")
    cap = cv2.VideoCapture(RTMP_URL)

    if not cap.isOpened():
        print(f"Error: Could not open video stream at {RTMP_URL}")
        return

    print("Stream connected. Starting capture loop...")

    last_capture_time = time.time()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to grab frame. Stream might have ended or encountered an issue.")
            # Optional: try to reconnect or break
            time.sleep(CAPTURE_INTERVAL) # Wait before retrying or exiting
            # Reconnect logic could go here
            # For now, let's try reopening
            cap.release()
            cap = cv2.VideoCapture(RTMP_URL)
            if not cap.isOpened():
                print("Failed to reconnect. Exiting.")
                break
            else:
                print("Reconnected to stream.")
                continue

        current_time = time.time()
        if current_time - last_capture_time >= CAPTURE_INTERVAL:
            process_frame(frame) # Use the unified processing function
            last_capture_time = current_time

        # Optional: Add a small delay to prevent high CPU usage if frame reading is very fast
        # time.sleep(0.01)

        # Optional: Display the stream (requires a GUI environment)
        # cv2.imshow('RTMP Stream', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

    # Release resources
    cap.release()
    # cv2.destroyAllWindows() # Only needed if using cv2.imshow
    print("Stream released.")

def run_testing_mode():
    """Runs the script in testing mode using local images."""
    print("Starting testing mode...")
    # Find image files (adjust patterns as needed)
    image_patterns = [os.path.join(TEST_IMAGE_DIR, f) for f in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"]]
    image_files = []
    for pattern in image_patterns:
        image_files.extend(glob.glob(pattern))

    if not image_files:
        print(f"Error: No image files found in {TEST_IMAGE_DIR}")
        return

    print(f"Found {len(image_files)} images to process.")

    for image_path in image_files:
        print(f"\n--- Loading image: {os.path.basename(image_path)} ---")
        frame = cv2.imread(image_path)

        if frame is None:
            print(f"Warning: Could not read image file: {image_path}. Skipping.")
            continue

        process_frame(frame) # Use the unified processing function

def main():
    if TESTING_MODE:
        run_testing_mode()
    else:
        run_rtmp_mode()

if __name__ == "__main__":
    main()
