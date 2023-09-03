# batch-video-encoding-automation

## Purpose
I wanted to reduce the file size of my video for long term storage by using AV1 encoding. Handbrake do not supported nested folder so I created a script that will do the conversion and maintain the folder structure (also handle the case of multiple file having the same name). The conversion takes a long time to compute so I added some temporary directory so that multiple computer can process same folder on a NAS. I also moved the procesed video so that I can reboot the machine and rerun the script without the concern of doing duplicate work.

I also wanted to get some metrics on the effectiveness of SVT-AV1. After I have to metric to prove that the conversion was worth it, I will replace the existing version with the converted version.

## How to use
I broke the process down to 2 steps
1. convert the video using `video_convert`
1. compare the video using `video_stats_comparator`

### How to use `video_convert`
#### Pre-req
get [HandBrakeCLI](https://handbrake.fr/downloads2.php)
For windows, put it in to the same directory with the script

#### Usage
1. update `original_directory` to your original directory (or other directory if needed)
1. update `backup quality.json` to your preferred settings or generate a setting using HandBrake GUI (require to update script and point to your json)
1. (Linux) comment out windows command and comment in linux command
1. run the script

### How to use `video_stats_comparator`
#### Pre-req
install [ffmpeg](https://ffmpeg.org/download.html#build-windows) and add it to env path

#### Usage
1. update `original_directory` and `mkv_directory` to your original and new directory
1. run the script
1. open `video_stats_comparison.csv`

#### video_stats_comparison.csv
This CSV provides
1. the VMAF score to compare the visual quality
1. the change in file size
1. the change in number of frames
