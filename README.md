# Video Parser with Audio Speedup and Conversion
This Python code processes a video file and applies 4x speedup to muted audio regions, while maintaining normal speed for audio with sound. The audio is also converted from 440hz to 432hz. The processed video and audio are combined into a single file.

## Dependencies
This code requires the moviepy library to be installed, which you can install using pip install moviepy.

## Usage
Place the video file you want to process in the same directory as the code and name it "videoInput.mp4".
Run the code using a Python 3 interpreter (e.g. python video_parser.py). The code will split the video into 45 chunks and process them in parallel on 45 threads. Each chunk will be processed separately and saved as a separate file.
Once all the chunks have been processed, the code will combine them into a single file named "432hzVideoOutput.mp4" in the same directory.

## How it Works
The video file is loaded using the moviepy library and split into 45 chunks for parallel processing.
Each chunk is processed in a separate thread using the process_chunk function.
The process_chunk function loads the video chunk, splits it into frames, and determines which frames have muted audio.
For frames with muted audio, the playback rate is set to 4x, and for frames with audio, the playback rate is set to 1x.
The frames are combined into a moviepy video clip, and the audio clip is extracted and processed using the process_audio_clip function, which converts the audio from 440hz to 432hz.
The processed video and audio clips are combined into a single clip using moviepy functions, and the clip is saved as a file with the prefix "output_" and the same file extension as the input file.
Once all the chunks have been processed, the output files are loaded and combined into a single clip using moviepy functions, and the clip is saved as a file named "432hzVideoOutput.mp4".
