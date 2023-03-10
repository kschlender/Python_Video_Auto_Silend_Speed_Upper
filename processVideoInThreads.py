import moviepy.editor as mp
import numpy as np
import threading

def process_audio_clip(audio_clip):
    # Modify audio to 432hz
    audio_clip = audio_clip.fx(mp.audio.change_speed, 432/440)
    return audio_clip

def process_video_clip(video_clip):
    # Split audio and video
    audio_clip = video_clip.audio
    video_clip = video_clip.without_audio()
    
    # Create mask for muted audio
    audio_mask = audio_clip.to_soundarray().max(axis=1) < 0.05
    
    # Create array of playback rates
    playback_rates = np.ones(len(audio_mask))
    playback_rates[audio_mask] = 4
    
    # Create array of video frames
    video_frames = []
    for i in range(len(playback_rates)):
        frame = video_clip.get_frame(i / video_clip.fps)
        video_frames.extend([frame] * int(playback_rates[i]))
    
    # Combine video frames and audio clip
    final_clip = mp.concatenate_videoclips([mp.ImageClip(frame) for frame in video_frames])
    final_clip = final_clip.set_audio(process_audio_clip(audio_clip))
    
    return final_clip

def process_chunk(chunk):
    # Load chunk and process video clip
    clip = mp.VideoFileClip(chunk)
    clip = process_video_clip(clip)
    
    # Save processed clip to output file
    output_filename = "output_" + chunk
    clip.write_videofile(output_filename, fps=clip.fps)
    
if __name__ == '__main__':
    # Split video into chunks for processing in parallel
    input_filename = "videoInput.mp4"
    video_clip = mp.VideoFileClip(input_filename)
    chunk_size = video_clip.duration / 45
    chunks = [(i*chunk_size, (i+1)*chunk_size) for i in range(45)]
    
    # Process chunks in parallel using threads
    threads = []
    for chunk in chunks:
        t = threading.Thread(target=process_chunk, args=(chunk,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to finish before continuing
    for t in threads:
        t.join()
    
    # Combine processed chunks into final output file
    output_filenames = ["output_chunk{}.mp4".format(i) for i in range(45)]
    final_clip = mp.concatenate_videoclips([mp.VideoFileClip(f) for f in output_filenames])
    final_clip = final_clip.set_audio(process_audio_clip(final_clip.audio))
    final_clip.write_videofile("432hzVideoOutput.mp4", fps=final_clip.fps)
