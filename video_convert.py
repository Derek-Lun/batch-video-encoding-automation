import os
import shutil
import subprocess
import random
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------
# Config
# ----------------------------

ROOT_DIRECTORY = Path(r"path/to/root")
OUTPUT_DIRECTORY = Path(r"path/to/output")
PROCESSED_DIRECTORY = Path(r"path/to/processed")
TEMP_DIRECTORY = Path(r"path/to/temp")

VIDEO_EXTENSIONS = {"3gp", "avi", "divx", "mp4", "mov", "wmv", "mpeg", "mts"}


# ----------------------------
# Helpers
# ----------------------------

def get_optimal_workers():
    cpu_count = os.cpu_count() or 4
    return max(1, cpu_count // 2)  # ffmpeg is CPU heavy


def map_path(input_file: Path, src_root: Path, dst_root: Path, new_ext=None):
    rel = input_file.relative_to(src_root)
    if new_ext:
        rel = rel.with_suffix(new_ext)
    return dst_root / rel


def ensure_parent_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


# ----------------------------
# File discovery
# ----------------------------

def find_movie_files(root_dir):
    movie_files = []
    for path in root_dir.rglob("*"):
        if path.is_file() and path.suffix.lower()[1:] in VIDEO_EXTENSIONS:
            movie_files.append(path)
    return movie_files


# ----------------------------
# FFmpeg conversion
# ----------------------------

def convert_to_h265(input_file: Path, output_file: Path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_file),
        "-c:v", "libx265",
        "-preset", "veryslow",
        "-crf", "20",
        "-c:a", "copy",
        str(output_file)
    ]

    print(f"🎬 Converting: {input_file}")

    result = subprocess.run(cmd)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed for {input_file}")


# ----------------------------
# Processing logic
# ----------------------------

def process_file(movie_file: Path):
    try:
        output_file = map_path(movie_file, ROOT_DIRECTORY, OUTPUT_DIRECTORY, ".mkv")
        temp_file = map_path(movie_file, ROOT_DIRECTORY, TEMP_DIRECTORY, ".mkv")
        processed_file = map_path(movie_file, ROOT_DIRECTORY, PROCESSED_DIRECTORY)

        # Skip if already done
        if output_file.exists():
            print(f"⏭️ Skipping (exists): {output_file}")
            return

        # ----------------------------
        # 🔥 CLAIM FILE (move before processing)
        # ----------------------------
        try:
            ensure_parent_dir(processed_file)
            shutil.move(str(movie_file), str(processed_file))
        except FileNotFoundError:
            # Another host already took it
            print(f"🔒 Skipped (taken by another host): {movie_file}")
            return
        except Exception as e:
            print(f"⚠️ Failed to claim file: {movie_file} -> {e}")
            return

        # Now we own this file
        claimed_file = processed_file

        # Ensure directories exist
        ensure_parent_dir(output_file)
        ensure_parent_dir(temp_file)

        # Convert
        convert_to_h265(claimed_file, temp_file)

        # Move temp → final
        shutil.move(str(temp_file), str(output_file))

        print(f"✅ Done: {claimed_file}")

    except Exception as e:
        print(f"❌ Failed: {movie_file} -> {e}")


# ----------------------------
# Main
# ----------------------------

def main():
    movie_files = find_movie_files(ROOT_DIRECTORY)

    if not movie_files:
        print("No movie files found.")
        return

    print(f"Found {len(movie_files)} video files.")

    # ----------------------------
    # 🔥 RANDOMIZE ORDER
    # ----------------------------
    random.seed(time.time())
    random.shuffle(movie_files)

    max_workers = get_optimal_workers()
    print(f"Using {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_file, f) for f in movie_files]

        for future in as_completed(futures):
            future.result()

    print("\n🎉 All done!")


if __name__ == "__main__":
    main()