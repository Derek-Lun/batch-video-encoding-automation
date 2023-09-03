import os
import csv
from moviepy.editor import VideoFileClip
import subprocess
import json

def change_percentage(original, new):
    return ((new - original) / original) * 100

def calculate_vmaf(original_file, mkv_file):
    try:
        vmaf_command = [
            'ffmpeg',
            '-i', original_file,
            '-i', mkv_file,
            '-filter_complex', '[0:v][1:v]libvmaf=log_fmt=json:log_path=vmaf.json',
            '-f', 'null', '-'
        ]
        
        subprocess.run(vmaf_command, check=True, capture_output=True)
        
        with open('vmaf.json', 'r') as vmaf_file:
            vmaf_data = vmaf_file.read()
        
        vm = json.loads(vmaf_data)
        os.remove('vmaf.json')
        
        return vm["pooled_metrics"]["vmaf"]["min"], vm["pooled_metrics"]["vmaf"]["max"], vm["pooled_metrics"]["vmaf"]["mean"], vm["pooled_metrics"]["vmaf"]["harmonic_mean"]
    except Exception as e:
        print(f"Error calculating VMAF score for {original_file} and {mkv_file}: {e}")
        return ("-", "-", "-", "-")

def compare_video_info(original_dir, mkv_dir, extensions):
    video_comparison = []
    
    for dirpath, _, filenames in os.walk(original_dir):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext[1:].lower() in extensions:
                original_file = os.path.join(dirpath, filename)
                mkv_file = os.path.join(mkv_dir, os.path.relpath(original_file, original_dir))
                mkv_file = os.path.splitext(mkv_file)[0] + ".mkv"
                
                if os.path.exists(mkv_file):
                    original_clip = VideoFileClip(original_file)
                    mkv_clip = VideoFileClip(mkv_file)
                    vmaf_min, vmaf_max, vmaf_mean, vmaf_harmonic_mean = calculate_vmaf(original_file, mkv_file)
                    
                    original_size = os.path.getsize(original_file)
                    mkv_size = os.path.getsize(mkv_file)
                    size_change_percentage = change_percentage(original_size, mkv_size)

                    original_duration = original_clip.duration
                    mkv_duration = mkv_clip.duration
                    duration_change_percentage = change_percentage(original_duration, mkv_duration)

                    original_frames = original_clip.reader.nframes
                    mkv_frames = mkv_clip.reader.nframes
                    frame_change_percentage = change_percentage(original_frames, mkv_frames)
                    
                    video_comparison.append((original_file, mkv_file, original_size, mkv_size, size_change_percentage, vmaf_min, vmaf_max, vmaf_mean, vmaf_harmonic_mean, original_duration, mkv_duration, duration_change_percentage, original_frames, mkv_frames, frame_change_percentage))
                    print(f"{original_file, mkv_file, original_size, mkv_size, size_change_percentage, vmaf_min, vmaf_max, vmaf_mean, vmaf_harmonic_mean, original_duration, mkv_duration, duration_change_percentage, original_frames, mkv_frames, frame_change_percentage}")
                    
                    original_clip.close()
                    mkv_clip.close()
                else:
                    print(f"MKV file not found for: {original_file}")
                    video_comparison.append((original_file, "MKV Missing", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"))
    
    return video_comparison

def write_to_csv(csv_file, data):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Original File", "MKV File", "Original Size (bytes)", "MKV Size (bytes)", "Size Change Percentage", "Minimum VMAF Score", "Maximum VMAF Score", "Mean VMAF Score", "Harmonic Mean VMAF Score", "Original Duration (s)", "MKV Duration (s)", "Duration Change Percentage", "Original Frames", "MKV Frames", "Frame Change Percentage"])
        for item in data:
            writer.writerow(item)

if __name__ == "__main__":
    # Specify the directory paths for the original video files and MKV files
    original_directory = r"path/to/original"
    mkv_directory = r"path/to/mkv"

    # Specify the video file extensions to look for
    video_extensions = ["mp4", "avi", "mpeg", "3gp", "mov", "wmv"]

    video_comparison_data = compare_video_info(original_directory, mkv_directory, video_extensions)

    # Write the comparison data to a CSV file
    csv_file_path = "video_stats_comparison.csv"
    write_to_csv(csv_file_path, video_comparison_data)

    print(f"Video info comparison data written to: {csv_file_path}")