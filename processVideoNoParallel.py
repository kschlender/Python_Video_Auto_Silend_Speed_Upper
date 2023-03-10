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

# load input video clip
clip = VideoFileClip(input_file)

# split the video into chunks and process each chunk
output_files = []
for i in tqdm(range(num_chunks)):
    # calculate start and end times for chunk
    start_time = i * chunk_duration
    end_time = start_time + chunk_duration

    # extract video clip for chunk
    chunk_clip = clip.subclip(start_time, end_time)

    # extract audio frames for chunk
    audio_frames = chunk_clip.audio.to_soundarray()

    # determine which frames have muted audio
    muted_audio_mask = (audio_frames.max(axis=1) < audio_threshold)

    # create list of playback rates for each frame
    rates = [4.0 if muted_audio_mask[i] else 1.0 for i in range(len(muted_audio_mask))]

    # create list of color clips for each frame
    color_clips = [ColorClip(size=(chunk_clip.w, chunk_clip.h), color=[0, 0, 0], duration=1.0 / chunk_clip.fps) for i in range(len(rates))]

    # combine color clips and playback rates into video clip
    video_clip = concatenate_videoclips([chunk_clip.set_fps(chunk_clip.fps * rate).subclip(i, i + 1) for i, rate in enumerate(rates)], padding=0, method='compose')

    # extract audio clip for chunk
    audio_clip = chunk_clip.audio.subclip(0, chunk_clip.duration)

    # process audio clip for chunk
    audio_clip = audio_clip.fx(AudioFileClip.set_fps, 43200)

    # combine video and audio clips for chunk
    video_clip = video_clip.set_audio(audio_clip)

    # save output file for chunk
    output_filename = f"output_{i:02d}{os.path.splitext(input_file)[1]}"
    video_clip.write_videofile(output_filename, audio_codec='aac', verbose=False)

    output_files.append(output_filename)

# combine output files into a single file
clips = [VideoFileClip(f) for f in output_files]
video_clip = concatenate_videoclips(clips)
audio_clip = CompositeAudioClip([clip.audio for clip in clips])
video_clip = video_clip.set_audio(audio_clip)

# save output file
output_filename = "432hzVideoOutput.mp4"
video_clip.write_videofile(output_filename, audio_codec='aac', verbose=False)
