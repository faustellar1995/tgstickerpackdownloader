# -*- coding: utf-8 -*-
"""
Media processing functions for converting MP4 to GIF or PNG.
"""

import os
import ffmpeg
import numpy as np
import moviepy.editor as mp
from zipfile import ZipFile
from moviepy.editor import VideoFileClip
import shutil

def frames_are_identical(clip, num_frames=10):
    """
    抽取视频的若干帧，检查它们是否完全相同。
    """
    duration = clip.duration
    frame_times = np.linspace(0, duration, num_frames)
    frames = [clip.get_frame(t) for t in frame_times]
    
    first_frame = frames[0]
    for frame in frames[1:]:
        if not np.array_equal(first_frame, frame):
            return False
    return True

def get_video_fps(video_path):
    """
    获取视频的帧率。
    """
    clip = mp.VideoFileClip(video_path)
    return clip.fps

def convert_mp4_to_gif(mp4_path, gif_path):
    clip = mp.VideoFileClip(mp4_path)
    width, height = clip.size
    fps = get_video_fps(mp4_path)
    (
        ffmpeg
        .input(mp4_path)
        .output(gif_path, vf=f'scale={width}:{height}:flags=lanczos', pix_fmt='yuv422p', r=fps)
        .run()
    )
    print(f'Converted {mp4_path} to {gif_path}')
    # yuv420p: 8-bit YUV 4:2:0
    # yuv422p: 8-bit YUV 4:2:2
    # yuv444p: 8-bit YUV 4:4:4
    # rgb24: 8-bit RGB
    # gray: 8-bit grayscale

def convert_mp4_to_png(mp4_path, png_path):
    clip = VideoFileClip(mp4_path)
    clip.save_frame(png_path)
    print(f'Converted {mp4_path} to {png_path}')

def convert_mp4_to_gif_or_png(mp4_path, gif_path, png_path):    
    # clip = VideoFileClip(mp4_path)
    # if frames_are_identical(clip):
    #     # 保存第一帧为PNG
    #     convert_mp4_to_png(mp4_path, png_path)
    # else:
    #     # 保存为GIF
    convert_mp4_to_gif(mp4_path, gif_path)

def batch_convert_mp4_to_gif_or_png(directory):
    gif_directory = os.path.join(directory, 'gif')
    img_directory = os.path.join(directory, 'img')
    
    # 创建gif和img子文件夹（如果不存在）
    if not os.path.exists(gif_directory):
        os.makedirs(gif_directory)
    if not os.path.exists(img_directory):
        os.makedirs(img_directory)

    # 遍历目录下的所有mp4文件并转换为gif或img
    for filename in os.listdir(directory):
        if filename.endswith('.mp4'):
            mp4_path = os.path.join(directory, filename)
            gif_filename = f"{os.path.splitext(filename)[0]}.gif"
            gif_path = os.path.join(gif_directory, gif_filename)
            img_filename = f"{os.path.splitext(filename)[0]}.png"
            img_path = os.path.join(img_directory, img_filename)
            
            # 检查目标文件是否已存在
            if os.path.exists(gif_path) or os.path.exists(img_path):
                print(f'{gif_path} or {img_path} already exists, skipping.')
                continue
            
            convert_mp4_to_gif_or_png(mp4_path, gif_path, img_path)
    
    # 复制所有webp文件到img_directory
    for filename in os.listdir(directory):
        if filename.endswith('.webp'):
            webp_path = os.path.join(directory, filename)
            new_webp_path = os.path.join(img_directory, filename)
            shutil.copy2(webp_path, new_webp_path)

    zip_filename = os.path.join(directory, 'converted_files.zip')
    with ZipFile(zip_filename, 'w') as zipf:
        for folder_name in [gif_directory, img_directory]:
            for foldername, subfolders, filenames in os.walk(folder_name):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, directory)
                    zipf.write(file_path, arcname)

    print(f'GIF and IMG files have been zipped into {zip_filename}')
