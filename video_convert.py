import os
import fnmatch
import shutil
from pathlib import Path

def find_movie_files(root_dir, extensions):
    movie_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if any(fnmatch.fnmatch(filename, f"*.{ext}") for ext in extensions):
                movie_files.append(os.path.join(dirpath, filename))
    return movie_files

def get_new_filepath(input_file, new_directory):
    return input_file.replace(original_directory, new_directory)

def convert_extension_to_mkv(input_file):
    return input_file[:-4] + ".mkv"

def convert_to_AV1(input_file, output_file):
    # command for windows. Require HandBrakeCLI.exe to exist in the same directory.
    command = "HandBrakeCLI.exe -v --preset-import-file \"backup quality.json\" --preset \"backup quality\"" + " -i \""+ input_file + "\" -o \"" + output_file + "\""
    # command for linux. Require HandBrakeCLI to be installed.
    # command = "flatpak run --command=HandBrakeCLI fr.handbrake.ghb -v --preset-import-file backup_quality.json --preset \"backup quality\"" + " -i \""+ input_file + "\" -o \"" + output_file + "\""
    print("command: " + command)
    print(os.system(command))

def make_dir(directory):
    try:
        os.makedirs(os.path.dirname(directory))
    except:
        print(os.path.dirname(directory) + " already created")

if __name__ == "__main__":
    original_directory = os.path.expanduser("e:/temp")
    processing_directory = original_directory + " processing"
    temp_directory = original_directory + " temp"
    processed_directory = original_directory + " processed"
    converted_directory = original_directory + " converted"

    # Specify the movie file extensions to look for
    movie_extensions = ["mp4", "avi", "mpeg", "3gp", "mov", "wmv"]

    movie_files = find_movie_files(original_directory, movie_extensions)

    # Display the list of movie files found
    if movie_files:
        print("Movie files found:" + str(len(movie_files)))
        for movie_file in movie_files:
            print("orignal video: " + movie_file)

            processing_file = get_new_filepath(movie_file, processing_directory)
            print("processing location: " + processing_file)
            make_dir(processing_file)

            temp_file = convert_extension_to_mkv(get_new_filepath(movie_file, temp_directory))
            print("temp location: " + temp_file)
            make_dir(temp_file)

            processed_file = get_new_filepath(movie_file, processed_directory)
            print("processed location: " + processed_file)
            make_dir(processed_file)

            converted_file = convert_extension_to_mkv(get_new_filepath(movie_file, converted_directory))
            print("output location: " + converted_file)
            make_dir(converted_file)

            shutil.move(movie_file, processing_file)
            convert_to_AV1(processing_file, temp_file)
            print(movie_file + "convert completed")

            shutil.move(processing_file, processed_file)
            shutil.move(temp_file, converted_file)
    else:
        print("No movie files found.")