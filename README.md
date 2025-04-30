# Drone AI

A project for analyzing video streams from drones using vision AI models.

## Overview

This application connects to an RTMP video stream, periodically captures frames, and sends them to OpenAI's GPT-4o vision model for analysis. It's designed to provide real-time insights about what the drone is seeing.

## Requirements

- Python 3.6+
- OpenCV
- OpenAI Python SDK
- python-dotenv

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
```

### Configuration Options

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `RTMP_URL` (required): The RTMP stream URL to connect to
- `OPENAI_PROMPT` (optional): The prompt to send to OpenAI with the image (default: "What is in this image?")
- `CAPTURE_INTERVAL` (optional): How often to capture and analyze frames in seconds (default: 5)

## Usage

Run the script with:

```
python drone-ai.py
```

The application will:
1. Connect to the specified RTMP stream
2. Capture frames at the defined interval
3. Send each captured frame to OpenAI's vision API
4. Print the AI analysis to the console

## Notes

- The application will attempt to reconnect if the stream is disconnected
- For displaying the video feed locally, uncomment the cv2.imshow sections in the code