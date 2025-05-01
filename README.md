# Drone AI

A project for analyzing video streams (from drones or local files) using vision AI models (OpenAI and YOLO).

## Overview

This application connects to an RTMP video stream (or reads local image files), periodically captures/reads frames, performs object detection using YOLOv11n, and sends the frames to OpenAI's GPT-4o vision model for broader analysis. It's designed to provide real-time insights about what the drone is seeing or analyze a set of test images.

## Features

- **Dual AI Analysis**: Utilizes both YOLO for fast object detection and OpenAI GPT-4o for detailed image description.
- **RTMP Stream Support**: Connects to live RTMP video streams.
- **Testing Mode**: Allows analysis of local image files for testing and development.
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

```
OPENAI_API_KEY=your_openai_api_key
RTMP_URL=rtmp://your-rtmp-server/live/key
OPENAI_PROMPT="What is in this image?"
CAPTURE_INTERVAL=5

# Testing Mode (Optional)
TESTING_MODE=true # Set to true to enable testing mode, false or omit for RTMP mode
TEST_IMAGE_DIR=./test_images # Path to the directory containing images for testing mode
```

### Configuration Options

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `RTMP_URL` (required if `TESTING_MODE` is false): The RTMP stream URL to connect to
- `OPENAI_PROMPT` (optional): The prompt to send to OpenAI with the image (default: "What is in this image?")
- `CAPTURE_INTERVAL` (optional): How often to capture/analyze frames in seconds (default: 5). In testing mode, this is the delay between processing each image.
- `TESTING_MODE` (optional): Set to `true` to enable testing mode, `false` or omit to use RTMP stream mode (default: `false`)
- `TEST_IMAGE_DIR` (required if `TESTING_MODE` is true): The path to the directory containing image files (`.jpg`, `.png`, etc.) to be processed in testing mode.

## Usage

Run the script with:

```
python drone-ai.py
```

The application will:
1. Connect to the specified RTMP stream **or** prepare to read from the test image directory based on `TESTING_MODE`
2. Capture/Read frames at the defined `CAPTURE_INTERVAL`
3. Perform object detection using YOLO and display results (bounding boxes on the image)
4. Send each captured frame to OpenAI's vision API
5. Print the OpenAI analysis to the console

## Notes

- In RTMP mode, the application will attempt to reconnect if the stream is disconnected
- YOLO results are displayed in a separate window (`results[0].show()`). Press any key in that window to proceed to the next frame/analysis
- For displaying the raw video feed locally (without YOLO boxes), uncomment the `cv2.imshow` sections in the RTMP mode code
