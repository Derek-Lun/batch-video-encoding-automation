import os
import csv
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------
# Helpers
# ----------------------------

def change_percentage(original, new):
    if original in (0, None):
        return 0
    return ((new - original) / original) * 100


def ffprobe_video_info(file_path):
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries",
            "stream=codec_name,width,height,nb_frames,r_frame_rate,duration",
            "-show_entries",
            "format=duration",
            "-of", "json",
            file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        streams = data.get("streams", [])
        if not streams:
            return {}

        stream = streams[0]

        # Duration
        duration = stream.get("duration")
        if duration is None:
            duration = data.get("format", {}).get("duration")

        duration = float(duration) if duration else None

        # FPS
        fps = None
        r_frame_rate = stream.get("r_frame_rate")
        if r_frame_rate and r_frame_rate != "0/0":
            num, den = map(int, r_frame_rate.split("/"))
            fps = num / den if den != 0 else None

        # Frame count
        nb_frames = stream.get("nb_frames")
        if nb_frames:
            nb_frames = int(nb_frames)
        elif fps and duration:
            nb_frames = round(fps * duration)
        else:
            nb_frames = None

        return {
            "codec": stream.get("codec_name", "unknown"),
            "width": stream.get("width"),
            "height": stream.get("height"),
            "resolution": (stream.get("width"), stream.get("height")),
            "duration": duration,
            "frames": nb_frames,
            "fps": fps
        }

    except Exception as e:
        print(f"ffprobe failed for {file_path}: {e}")
        return {}


# ----------------------------
# Core processing
# ----------------------------

def process_file(original_file, mkv_file):
    try:
        if not os.path.exists(mkv_file):
            return (original_file, "MKV Missing", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-")

        original_info = ffprobe_video_info(original_file)
        mkv_info = ffprobe_video_info(mkv_file)

        original_size = os.path.getsize(original_file)
        mkv_size = os.path.getsize(mkv_file)
        size_change_percentage = change_percentage(original_size, mkv_size)

        original_duration = original_info.get("duration")
        mkv_duration = mkv_info.get("duration")
        duration_change_percentage = change_percentage(original_duration, mkv_duration)

        original_frames = original_info.get("frames")
        mkv_frames = mkv_info.get("frames")
        frame_change_percentage = change_percentage(original_frames, mkv_frames)

        original_resolution = original_info.get("resolution")
        mkv_resolution = mkv_info.get("resolution")

        original_codec = original_info.get("codec", "unknown")
        mkv_codec = mkv_info.get("codec", "unknown")

        return (
            original_file, mkv_file,
            original_size, mkv_size, size_change_percentage,
            "-", "-", "-", "-",  # VMAF placeholders
            original_duration, mkv_duration, duration_change_percentage,
            original_frames, mkv_frames, frame_change_percentage,
            original_resolution, mkv_resolution,
            original_codec, mkv_codec
        )

    except Exception as e:
        print(f"Error processing {original_file}: {e}")
        return (original_file, "ERROR", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-")


# ----------------------------
# Main comparison
# ----------------------------

def compare_video_info(original_dir, mkv_dir, extensions, max_workers=8):
    tasks = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for dirpath, _, filenames in os.walk(original_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1][1:].lower()
                if ext in extensions:
                    original_file = os.path.join(dirpath, filename)

                    mkv_file = os.path.join(mkv_dir,os.path.relpath(original_file, original_dir))
                    mkv_file = os.path.splitext(mkv_file)[0] + ".mkv"

                    tasks.append(executor.submit(process_file, original_file, mkv_file))

        results = []
        for future in as_completed(tasks):
            result = future.result()
            print(result)
            results.append(result)

    return results


# ----------------------------
# CSV writer
# ----------------------------

def write_to_csv(csv_file, data):
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Original File", "MKV File",
            "Original Size (bytes)", "MKV Size (bytes)", "Size Change %",
            "Min VMAF", "Max VMAF", "Mean VMAF", "Harmonic Mean VMAF",
            "Original Duration (s)", "MKV Duration (s)", "Duration Change %",
            "Original Frames", "MKV Frames", "Frame Change %",
            "Original Resolution", "MKV Resolution",
            "Original Codec", "MKV Codec"
        ])
        writer.writerows(data)


# ----------------------------
# Entry point
# ----------------------------

if __name__ == "__main__":
    original_directory = r"path/to/original"
    mkv_directory = r"path/to/mkv"

    video_extensions = ["3gp", "avi", "divx", "mp4", "mov", "wmv", "mpeg", "mts"]

    data = compare_video_info(original_directory, mkv_directory, video_extensions, max_workers=8)

    output_file = "video_stats_comparison.csv"
    write_to_csv(output_file, data)

    print(f"\nDone! Results saved to: {output_file}")
