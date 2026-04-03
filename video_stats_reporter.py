import os
import csv
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------
# Configurable worker tuning
# ----------------------------

def get_optimal_workers(user_defined=None):
    if user_defined:
        return user_defined

    cpu_count = os.cpu_count() or 4
    return min(cpu_count * 2, 16)


# ----------------------------
# ffprobe helper
# ----------------------------

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
        duration = stream.get("duration") or data.get("format", {}).get("duration")
        duration = float(duration) if duration else None

        # FPS
        fps = None
        r_frame_rate = stream.get("r_frame_rate")
        if r_frame_rate and r_frame_rate != "0/0":
            num, den = map(int, r_frame_rate.split("/"))
            fps = num / den if den != 0 else None

        # Frame count
        nb_frames = stream.get("nb_frames")
        if nb_frames and nb_frames != "N/A":
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
# File processing
# ----------------------------

def process_file(file_path):
    try:
        info = ffprobe_video_info(file_path)

        size = os.path.getsize(file_path)

        return (
            file_path,
            size,
            info.get("duration"),
            info.get("frames"),
            info.get("fps"),
            info.get("resolution"),
            info.get("codec")
        )

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return (file_path, "ERROR", "-", "-", "-", "-", "-")


# ----------------------------
# Main scan
# ----------------------------

def scan_videos(directory, extensions, max_workers=None):
    max_workers = get_optimal_workers(max_workers)
    print(f"Using {max_workers} workers...")

    tasks = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                ext = os.path.splitext(filename)[1][1:].lower()
                if ext in extensions:
                    file_path = os.path.join(dirpath, filename)
                    tasks.append(executor.submit(process_file, file_path))

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
            "File",
            "Size (bytes)",
            "Duration (s)",
            "Frames",
            "FPS",
            "Resolution",
            "Codec"
        ])
        writer.writerows(data)


# ----------------------------
# Entry point
# ----------------------------

if __name__ == "__main__":
    original_directory = r"path/to/video"

    video_extensions = ["3gp", "avi", "divx", "mp4", "mkv", "mov", "wmv", "mpeg", "mts"]

    data = scan_videos(video_directory, video_extensions)

    output_file = "video_stats.csv"
    write_to_csv(output_file, data)

    print(f"\nDone! Results saved to: {output_file}")