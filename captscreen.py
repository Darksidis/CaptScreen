#!/usr/bin/env python3
"""
CaptScreen - Simple screen recorder for Windows
Recording: press Enter to start/stop
Timer: specify duration in minutes at startup (0 = unlimited)
"""

import cv2
import mss
import numpy as np
import time
import threading
import sys
from datetime import datetime

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.paused = False
        self.writer = None
        self.start_time = None
        self.duration = 0  # in seconds, 0 = unlimited
        self.output_file = None
        
    def get_output_filename(self):
        """Generates filename based on current time"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"recording_{timestamp}.mp4"
    
    def start_recording(self, duration_minutes=0):
        """Starts screen recording"""
        if self.recording:
            print("Recording is already in progress!")
            return
            
        self.duration = duration_minutes * 60 if duration_minutes > 0 else 0
        self.output_file = self.get_output_filename()
        
        # Get screen dimensions
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            self.width = monitor["width"]
            self.height = monitor["height"]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(
            self.output_file, 
            fourcc, 
            20.0,  # FPS
            (self.width, self.height)
        )
        
        self.recording = True
        self.start_time = time.time()
        
        print(f"\n{'='*50}")
        print(f"RECORDING STARTED: {self.output_file}")
        if self.duration > 0:
            print(f"Duration: {duration_minutes} minute(s)")
            print(f"Ends at: {datetime.fromtimestamp(self.start_time + self.duration).strftime('%H:%M:%S')}")
        else:
            print("Press Enter to stop recording")
        print(f"{'='*50}\n")
        
        # Start recording in separate thread
        record_thread = threading.Thread(target=self._record_loop)
        record_thread.daemon = True
        record_thread.start()
        
    def _record_loop(self):
        """Main screen capture loop"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            
            while self.recording:
                # Check timer
                if self.duration > 0:
                    elapsed = time.time() - self.start_time
                    if elapsed >= self.duration:
                        print(f"\nTimer expired! Recording stopped.")
                        self.stop_recording()
                        break
                
                # Capture frame
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                
                # Convert BGRA -> BGR for OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Write frame
                if self.writer is not None:
                    self.writer.write(frame)
                
                # Display recording time
                if self.duration > 0:
                    remaining = self.duration - (time.time() - self.start_time)
                    mins, secs = divmod(int(remaining), 60)
                    print(f"\rRemaining: {mins:02d}:{secs:02d}", end="", flush=True)
                else:
                    elapsed = time.time() - self.start_time
                    mins, secs = divmod(int(elapsed), 60)
                    print(f"\rRecording: {mins:02d}:{secs:02d}", end="", flush=True)
                
                # Small delay for stability
                time.sleep(0.05)
    
    def stop_recording(self):
        """Stops recording"""
        if not self.recording:
            return
            
        self.recording = False
        
        if self.writer:
            self.writer.release()
            self.writer = None
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        mins, secs = divmod(int(elapsed), 60)
        
        print(f"\n\n{'='*50}")
        print(f"RECORDING STOPPED")
        print(f"File: {self.output_file}")
        print(f"Duration: {mins:02d}:{secs:02d}")
        print(f"{'='*50}\n")


def main():
    print("\n" + "="*50)
    print("   CaptScreen - Screen Recorder")
    print("="*50)
    
    recorder = ScreenRecorder()
    
    # Ask for duration
    print("\nEnter recording duration in minutes (0 = unlimited):")
    try:
        duration_input = input(">>> ").strip()
        duration = int(duration_input) if duration_input else 0
    except ValueError:
        duration = 0
        print("Invalid input, recording without time limit")
    
    print("\nPress Enter to start recording...")
    input()
    
    recorder.start_recording(duration)
    
    # Wait for Enter to stop (if no timer)
    if duration == 0:
        input()  # Wait for Enter press
        recorder.stop_recording()
    else:
        # Wait until recording finishes by timer
        while recorder.recording:
            time.sleep(0.1)
    
    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
