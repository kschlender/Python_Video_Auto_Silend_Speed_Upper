import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from tqdm import tqdm

# input file
input_file = "videoInput.mp4"

# audio threshold (determines which frames have muted audio)
audio_threshold = 0.01

# chunk size (in seconds)
chunk_duration = 5

# number of chunks to split the video into
num_chunks = 45

# load the video clip
clip = VideoFileClip(input_file)

# get the total duration of the video clip
total_duration = clip.duration

# determine the start and end times for each chunk
chunk_start_times = [i * chunk_duration for i in range(num_chunks)]
chunk_end_times = [(i + 1) * chunk_duration for i in range(num_chunks)]
chunk_end_times[-1] = total_duration

# process each chunk of the video
output_files = []
for i in tqdm(range(num_chunks)):
    # determine the start and end times for this chunk
    start_time = chunk_start_times[i]
    end_time = chunk_end_times[i]

    # extract the chunk of the video
    chunk = clip.subclip(start_time, end_time)

    # get audio frames
    audio_frames = chunk.audio.to_soundarray()

    # determine which frames have muted audio
    muted_audio_mask = (audio_frames.max(axis=1) < audio_threshold)

    # create list of playback rates for each frame
    rates = [4.0 if muted_audio_mask[j] else 1.0 for j in range(len(muted_audio_mask))]

    # create list of color clips for each frame
    color_clips = [ColorClip(size=(chunk.w, chunk.h), color=[0, 0, 0], duration=1.0 / chunk.fps) for k in range(len(rates))]

    # combine color clips and playback rates into video clip
    video_clip = concatenate_videoclips([chunk.set_fps(chunk.fps * rates[l]).subclip(l, l + 1) for l in range(len(rates))], method="compose")

    # extract audio clip
    audio_clip = chunk.audio.subclip(0, chunk.duration)

    # process audio clip
    audio_clip = process_audio_clip(audio_clip)

    # combine video and audio clips
    video_clip = video_clip.set_audio(audio_clip)

    # save output file
    output_filename = f"output_{i:02d}{os.path.splitext(input_file)[1]}"
    video_clip.write_videofile(output_filename, audio_codec='aac', verbose=False)

    # add output file to list of output files
    output_files.append(output_filename)

# combine output files into a single file
clips = [VideoFileClip(f) for f in output_files]
video_clip = concatenate_videoclips(clips)
audio_clip = CompositeAudioClip([clip.audio for clip in clips])
video_clip = video_clip.set_audio(audio_clip)

# save output file
output_filename = "432hzVideoOutput.mp4"
video_clip.write_videofile(output_filename, audio_codec='aac', verbose=False)
