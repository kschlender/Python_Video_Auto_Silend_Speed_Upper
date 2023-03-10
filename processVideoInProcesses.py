import os
import multiprocessing
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from tqdm import tqdm

# function to process a video chunk
def process_chunk(chunk_idx):
    # load video chunk
    start_time = chunk_idx * chunk_duration
    end_time = start_time + chunk_duration
    clip = VideoFileClip(input_file).subclip(start_time, end_time)

    # get audio frames
    audio_frames = clip.audio.to_soundarray()

    # determine which frames have muted audio
    muted_audio_mask = (audio_frames.max(axis=1) < audio_threshold)

    # create list of playback rates for each frame
    rates = [4.0 if muted_audio_mask[i] else 1.0 for i in range(len(muted_audio_mask))]

    # create list of color clips for each frame
    color_clips = [ColorClip(size=(clip.w, clip.h), color=[0, 0, 0], duration=1.0 / clip.fps) for i in range(len(rates))]

    # combine color clips and playback rates into video clip
    video_clip = CompositeVideoClip([clip.set_fps(clip.fps * rate).subclip(i, i + 1) for i, rate in enumerate(rates)], size=clip.size)

    # extract audio clip
    audio_clip = clip.audio.subclip(0, clip.duration)

    # process audio clip
    audio_clip = process_audio_clip(audio_clip)

    # combine video and audio clips
    video_clip = video_clip.set_audio(audio_clip)

    # save output file
    output_filename = f"output_{chunk_idx:02d}{os.path.splitext(input_file)[1]}"
    video_clip.write_videofile(output_filename, audio_codec='aac', verbose=False)

    return output_filename

# function to process audio clip
def process_audio_clip(audio_clip):
    # convert audio from 440hz to 432hz
    audio_clip = audio_clip.fx(AudioFileClip.set_fps, 43200)
    return audio_clip

# input file
input_file = "videoInput.mp4"

# audio threshold (determines which frames have muted audio)
audio_threshold = 0.01

# chunk size (in seconds)
chunk_duration = 5

# number of chunks to split the video into
num_chunks = 45

# split the video into chunks and process each chunk in a separate process
pool = multiprocessing.Pool(processes=num_chunks)
results = []
for i in tqdm(range(num_chunks)):
    result = pool.apply_async(process_chunk, args=(i,))
    results.append(result)

# wait for all processes to finish
output_files = [result.get() for result in results]

# combine output files into a single file
output_files = sorted([f for f in os.listdir() if f.startswith("output_")])
clips = [VideoFileClip(f) for f in output_files]
video_clip = concatenate_videoclips(clips)
audio_clip = CompositeAudioClip([clip.audio for clip in clips])
video_clip = video_clip.set_audio(audio_clip)

# save output file
output_filename = "432hzVideoOutput.mp4"
video_clip.write_videofile(output_filename, audio_codec='aac', verbose=False)
