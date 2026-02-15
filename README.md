# CaptScreen - Simple screen recording for Windows

A console program for capturing a screen with minimal functionality. It was tested on Windows 10/11.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python captscreen.py
```

### Management

1. **Program start** - enter the recording duration in minutes (0 = unlimited)
2. **Start recording** - press Enter
3. **Stop recording** - press Enter (if timer is not set)

### Examples

- **Recording 2 hours**: Enter `120` at startup
- **Recording 3 hours**: Enter `180` at startup  
- **Manual stop**: Enter `0` and press Enter to start/stop

### Output files

The files are saved to the current folder named:
``
recording_YYYY-MM-DD_HH-MM-SS.mp4
```

## Requirements

- Windows 10/11

- Python 3.8+
