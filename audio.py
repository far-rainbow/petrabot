import ffmpeg
import img

def add_mp3_to_video(video, audio, VIDEO_DIR, SOUND_DIR):
    ffmpeg_tmp_video_name = VIDEO_DIR+'ffpmeg_'+video
    sound = ffmpeg.input(SOUND_DIR+audio).audio
    video = ffmpeg.input(VIDEO_DIR+video)
    out = ffmpeg.concat(video, sound, v=1, a=1).output(ffmpeg_tmp_video_name,
                                                       vcodec='libx265').run()
    return ffmpeg_tmp_video_name