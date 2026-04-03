import shutil
from pathlib import Path

# ----------------------------
# Config
# ----------------------------

ROOT_DIRECTORY = Path(r"path/to/root")
OUTPUT_DIRECTORY = Path(r"path/to/output")

VIDEO_EXTENSIONS = {"3gp", "avi", "divx", "mp4", "mov", "wmv", "mpeg", "mts"}


# ----------------------------
# Helpers
# ----------------------------

def find_movie_files(root_dir):
    return [
        path for path in root_dir.rglob("*")
        if path.is_file() and path.suffix.lower()[1:] in VIDEO_EXTENSIONS
    ]


def get_output_file(input_file):
    rel = input_file.relative_to(ROOT_DIRECTORY)
    return OUTPUT_DIRECTORY / rel


# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":
    movie_files = find_movie_files(ROOT_DIRECTORY)

    if not movie_files:
        print("No movie files found.")
    else:
        print(f"Movie files found: {len(movie_files)}")

        for movie_file in movie_files:
            print(f"Original: {movie_file}")

            output_file = get_output_file(movie_file)
            print(f"Copy to: {output_file}")

            # Ensure directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Skip if already copied
            if output_file.exists():
                print(f"⏭️ Skipping (exists): {output_file}")
                continue

            try:
                shutil.copy2(movie_file, output_file)
                print(f"✅ Copied")
            except Exception as e:
                print(f"❌ Failed: {movie_file} -> {e}")