import subprocess
from PIL import Image
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "bin", "ffmpeg.exe")

def remove_metadata(input_path: str, output_path: str):
    with Image.open(input_path) as img:
        data = list(img.getdata())
        img_no_metadata = Image.new(img.mode, img.size)
        img_no_metadata.putdata(data)
        img_no_metadata.save(output_path)

def add_gaussian_noise(input_path: str, output_path: str, noise_level: float = 0.01):
    image = Image.open(input_path).convert("RGB")
    np_image = np.array(image)
    mean, stddev = 0, noise_level * 255
    noise = np.random.normal(mean, stddev, np_image.shape).astype(np.int16)
    noisy_image = np.clip(np_image + noise, 0, 255).astype(np.uint8)
    Image.fromarray(noisy_image).save(output_path)

def add_gaussian_noise_to_video(input_path: str, output_path: str, noise_level: float = 0.01):
    noise_filter = f"noise=alls={noise_level * 100}:allf=t+u"
    command = [
        FFMPEG_PATH, "-i", input_path, "-vf", noise_filter, "-c:v", "libx264", "-preset", "fast", "-c:a", "copy", output_path
    ]
    subprocess.run(command, check=True)

def remove_video_metadata(input_path: str, output_path: str):
    command = [
        FFMPEG_PATH, "-i", input_path, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", output_path
    ]
    subprocess.run(command, check=True)
