import cv2
import time
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
RTMP_URL = os.getenv("RTMP_URL", "rtmp://192.168.158.143/live/key")
# Make sure to set the OPENAI_API_KEY environment variable
# You can get one from https://platform.openai.com/account/api-keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# What do you want to ask the AI about the image?
OPENAI_PROMPT = os.getenv("OPENAI_PROMPT", "What is in this image?") # Default prompt if not set
# How often to capture and send frame (in seconds)
CAPTURE_INTERVAL_STR = os.getenv("CAPTURE_INTERVAL", "5") # Default interval if not set

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.")
    exit()

if not RTMP_URL:
    print("Error: RTMP_URL environment variable not set.")
    exit()

try:
    CAPTURE_INTERVAL = float(CAPTURE_INTERVAL_STR)
except ValueError:
    print(f"Error: Invalid value for CAPTURE_INTERVAL environment variable: '{CAPTURE_INTERVAL_STR}'. Must be a number.")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY)

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

def main():
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
            print(f"Capturing frame at {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Encode image
            base64_image = encode_image_to_base64(frame)

            # Analyze image
            print("Sending frame to OpenAI for analysis...")
            description = analyze_image_with_openai(base64_image)

            if description:
                print("\n--- OpenAI Analysis Result ---")
                print(description)
                print("-----------------------------\n")

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

if __name__ == "__main__":
    main()
