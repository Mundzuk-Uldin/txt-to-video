from TextSplitter import TextReader
from TextToSpeech import AudioConverter
from ImageGetter import GoogleDownloader
from VideoCreator import VideoMaker
import moviepy.editor as mp
import multiprocessing
import argparse
import os


program = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100))
program.add_argument('-t', '--target', help='Select the document to read', dest='text_file',
                     nargs='?', type=str, default='Input/Generic.txt')
program.add_argument('-i', '--image-dir', help='Directory where images are stored', dest='image_path',
                     nargs='?', type=str, default='Images/')
program.add_argument('-a', '--audio-dir', help='Directory where audios are stored', dest='audio_dir',
                     nargs='?', type=str, default='Audios/')
program.add_argument('-r', '--resize-size', help='The max size image can have', dest='resize_size',
                     nargs='?', type=int, default=900)
program.add_argument('-fps', '--frames-per-second', help='Frames per second', dest='fps',
                     nargs='?', type=int, default=4)
program.add_argument('-g', '--gimmick',
                     help='The gimmick the images will follow Ex: if gimmick is anime all images will be anime related',
                     dest='gimmick', nargs='?', type=str, default="")
program.add_argument('-b', '--background-music', help='Location of the background music. '
                                                      'MUST BE AUDIO FILE',
                     dest='music_background', nargs='*', type=str, default='')
program.add_argument('-o', '--output', help='Select your output file. Must be mp4.', dest='output_file',
                     nargs='?', type=str, default='video.mp4')
program.add_argument('-sk', '--skip-adjusting', default=False, action='store_true', dest="skip_adjusting",
                     help="Skips adjusting the audio for background music and uses your audio file as it is")
program.add_argument('-v', '--volume-adjust', help='Adjust volume to a float. Default value is -30',
                     dest='volume_adjust', nargs='?', type=float, default=-30.0)

parser = program.parse_args()

image_path = parser.image_path
audio_path = parser.audio_dir
text_file = parser.text_file
resize_size = parser.resize_size
fps = parser.fps
gimmick = parser.gimmick
music_background = parser.music_background
output_file = parser.output_file
skip_adjusting = parser.skip_adjusting
volume_adjust = parser.volume_adjust

if gimmick:
    gimmick += " "

text_reader = TextReader(text_file)
sentences_list = text_reader.read_and_separate_sentences()

video_creator = VideoMaker()
Debug = False
relevant_word = text_reader.most_relevant_word()


def create_dir(*args):
    for arg in args:
        if not os.path.exists(arg):
            os.makedirs(arg)


create_dir(image_path, audio_path, "Background_Music/")
if not Debug:
    video_creator.folder_cleaning(image_path, audio_path)
    AudioConverter.convert_audio(sentences_list, audio_path)
    GoogleDownloader.download_images([f + gimmick for f in relevant_word], image_path)

images, audios = video_creator.folder_scanning(image_path, audio_path)
images = video_creator.add_fallbacks(len(sentences_list), images)
pil_images = video_creator.images_to_pil(images, resize_size)
audios = video_creator.audios_to_afc(audios)

clips_with_audio = video_creator.make_composite_list(pil_images, audios, sentences_list)
concat_clip = mp.concatenate_videoclips(clips_with_audio, method="compose")
thread_count = multiprocessing.cpu_count()
if music_background:
    audio_background_path = AudioConverter.adjust_audio(volume_adjust, skip_adjusting, *music_background)
    audio_background = [mp.AudioFileClip(f) for f in audio_background_path]
    final_audio = mp.CompositeAudioClip([concat_clip.audio] + audio_background)
    # Set the duration of the final_audio to match the duration of the video
    final_audio = final_audio.subclip(0, concat_clip.duration)
    concat_clip = concat_clip.set_audio(final_audio)
    for f in audio_background_path:
        if os.path.isfile(f) and not skip_adjusting:
            os.remove(f)

concat_clip.write_videofile(output_file, fps=fps, remove_temp=True, codec="libx264",
                            audio_codec="aac", threads=thread_count)
