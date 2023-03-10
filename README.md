# Python_Video_Auto_Silend_Speed_Upper
This Python code processes a video file called "videoInput.mp4" and applies 4x speedup to muted audio regions, while maintaining normal speed for audio with sound. The audio is also converted from 440hz to 432hz. The video is split into 45 chunks, which are processed in parallel on 45 threads, then combined into a single file named "432hz....mp4".
