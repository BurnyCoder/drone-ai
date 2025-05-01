# Drone AI

A project for analyzing video streams (from drones or local files) using vision AI models (OpenAI and YOLO).

## Overview

This application connects to an RTMP video stream (or reads local image files), periodically captures/reads frames, performs object detection using YOLOv11n, and sends the frames to OpenAI's GPT-4o vision model for broader analysis. It's designed to provide real-time insights about what the drone is seeing or analyze a set of test images.

## Features

- **Dual AI Analysis**: Utilizes both YOLOv11n for fast object detection and OpenAI GPT-4o for detailed image description.
- **RTMP Stream Support**: Connects to live RTMP video streams.
- **Testing Mode**: Allows analysis of local image files for testing and development.
- **Conditional OpenAI Analysis**: Option to send frames to OpenAI only if YOLO detects a person.
- **Configurable**: Settings managed via a `.env` file.

## Before installation

For DJI Mini 4 Pro drone, setup Monaserver and streaming using RTMP like in https://www.youtube.com/watch?v=ykf3B57elU0

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root directory with the following variables:

```dotenv
# Required: Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key

# Required if TESTING_MODE=false: The RTMP stream URL
RTMP_URL=rtmp://your-rtmp-server/live/key

# Optional: Prompt for OpenAI Vision API
OPENAI_PROMPT="What is in this image?"

# Optional: Interval (seconds) between frame captures/processing
CAPTURE_INTERVAL=5

# Optional: Enable Testing Mode (default: false)
# Set to true to read from TEST_IMAGE_DIR instead of RTMP stream
TESTING_MODE=false

# Optional: Directory for test images (required if TESTING_MODE=true)
TEST_IMAGE_DIR=./test_images

# Optional: OpenAI Analysis Condition (default: true)
# Set to true to only send images to OpenAI if YOLO detects a 'person'
# Set to false to always send images to OpenAI after YOLO analysis
OPENAI_CONDITION_PERSON=true
```

### Configuration Options

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `RTMP_URL` (required if `TESTING_MODE` is false): The RTMP stream URL to connect to
- `OPENAI_PROMPT` (optional): The prompt to send to OpenAI with the image (default: "What is in this image?")
- `CAPTURE_INTERVAL` (optional): How often to capture/analyze frames in seconds (default: 5). In testing mode, this acts as a delay between processing each image file.
- `TESTING_MODE` (optional): Set to `true` to enable testing mode. Defaults to `false` (RTMP stream mode) if omitted.
- `TEST_IMAGE_DIR` (required if `TESTING_MODE` is `true`): The path to the directory containing image files (`.jpg`, `.jpeg`, `.png`, etc.) to be processed in testing mode.
- `OPENAI_CONDITION_PERSON` (optional): Set to `true` to only send images to OpenAI if YOLO detects a person. Set to `false` to always send the image to OpenAI after YOLO analysis. Defaults to `true` if omitted.

## Usage

Run the script with:

```bash
python drone-ai.py
```

The application will:
1. Connect to the specified RTMP stream **or** prepare to read from the test image directory based on `TESTING_MODE`
2. Capture/Read frames at the defined `CAPTURE_INTERVAL`
3. Perform object detection using YOLOv11n. A window will pop up showing the frame with bounding boxes. Close this window or press a key to continue.
4. Conditionally (based on `OPENAI_CONDITION_PERSON` and whether a person was detected by YOLO) or unconditionally send the captured frame to OpenAI's vision API.
5. Print the OpenAI analysis (if performed) to the console.
6. Repeat for the next frame/image or until the stream ends/script is stopped.

## Notes

- In RTMP mode, the application will attempt to reconnect if the stream is disconnected
- YOLO results are displayed in a separate window using `results[0].show()`. You need to interact with this window (e.g., close it or press a key) for the script to proceed to the next frame or OpenAI analysis step.
- For displaying the raw video feed locally (without YOLO boxes), uncomment the `cv2.imshow` sections in the RTMP mode code (requires a GUI environment).

## Todo

- Gemini support
- Controlling drone inputs accordingly, not just analyzing videostream