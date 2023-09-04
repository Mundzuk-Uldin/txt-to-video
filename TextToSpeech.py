from gtts import gTTS
import os
from pydub import AudioSegment


def balance_volume(audio_fixed, volume_adjust):
    """
    Adjusts the volume of the background music (audio_fixed) to always be -30 dBFS.

    :param audio_fixed: The background music.
    :param volume_adjust: The value the volume will be.
    :return: Adjusted volume level for audio_fixed.
    """
    desired_dBFS = volume_adjust
    adjustment = desired_dBFS - audio_fixed.dBFS

    return audio_fixed + adjustment


class AudioConverter:
    @staticmethod
    def convert_audio(sentences_list, output_directory):
        for idx, sentence in enumerate(sentences_list):
            tts = gTTS(text=sentence, lang='en')
            audio_file_path = os.path.join(output_directory, f"{idx}.mp3")
            tts.save(audio_file_path)

            # Convert MP3 to WAV
            sound = AudioSegment.from_mp3(audio_file_path)
            sound.export(os.path.join(output_directory, f"{idx}.wav"), format="wav")

            # Optionally, delete the intermediate MP3 file
            os.remove(audio_file_path)

    @staticmethod
    def adjust_audio(volume_adjust, skip=False, *args):
        if skip:
            return args
        filenames = []
        for i, fix_audio in enumerate(args):
            extension = fix_audio.split(".")[1]
            audio_fixed = AudioSegment.from_file(fix_audio, format=extension)
            audio_fixed = balance_volume(audio_fixed, volume_adjust)
            filename = f"Background_Music/fixed_audio{i}.{extension}"
            audio_fixed.export(filename, format=extension)
            filenames.append(filename)
        return filenames
