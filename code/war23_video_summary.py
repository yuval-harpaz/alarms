# sudo apt-get install exiftool
# pip install pyexiftool
import os
# import exiftool
from glob import glob
import numpy as np
import pandas as pd
from easygui import diropenbox
import cv2
from matplotlib import pyplot as plt
from scipy.signal import find_peaks, medfilt
default_path = '/media/innereye/KINGSTON/War/'
if os.path.isdir(default_path):
    os.chdir('/home/innereye/Videos')
else:
    default_path = None
message = "Select a folder to process"
title = "oct7database"
current_path = diropenbox(message, None, default_path)
os.chdir(current_path)
files = glob('*.mp4')
for ii in range(len(files)):
    file = files[ii]
    # use cv2 to open video, assign nans to black or white pixels, then compute sum color difference between frames
    cap = cv2.VideoCapture(file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Processing {file} with {n_frames} frames at {int(fps)} FPS, width {width}, height {height}")
    frame_diffs = []
    prev_frame = np.zeros((height, width, 3))
    # prev_frame[:] = np.nan

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if len(frame_diffs) == 0:
            frame_diffs.append(0)
        else:
            # compute the difference between the current frame and the previous frame
            # diff = cv2.absdiff(frame, prev_frame)
            frame = frame.astype(float)
            # mask = (frame == 0) | (frame == 255) | (prev_frame == 0) | (prev_frame == 255)
            # diff = np.sum(np.abs(frame[~mask] - prev_frame[~mask]))
            diff = np.sum(np.abs((frame - prev_frame) > 10))
            frame_diffs.append(diff)
        prev_frame = frame.copy()
    cap.release()
    frame_diffs = np.array(frame_diffs)
    # Smooth the frame differences using a median filter
    frame_diffs_filt = medfilt(frame_diffs, kernel_size=3)
    # Find peaks in the smoothed frame differences
    peaks, _ = find_peaks(frame_diffs_filt, width=5, prominence=np.median(frame_diffs_filt)*2)
    fig = plt.figure()
    plt.plot(frame_diffs)
    plt.plot(frame_diffs_filt, 'g')
    plt.plot(peaks, frame_diffs_filt[peaks], 'r^')
    plt.ylabel('Frame Difference')
    plt.xlabel('Frame Number')
    plt.title(f'Diff peaks in video: {file}')
    plt.savefig(file.replace('.mp4', '_peaks.png'))
    # save peak frames as jpg
    for peak in peaks:
        cap = cv2.VideoCapture(file)
        cap.set(cv2.CAP_PROP_POS_FRAMES, peak)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(file.replace('.mp4', f'_{peak}.jpg'), frame)
        cap.release()


