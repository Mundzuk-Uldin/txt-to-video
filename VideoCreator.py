import os
import PIL.Image
import PIL.ImageChops
import moviepy.editor as mp
import numpy as np
from moviepy.editor import CompositeVideoClip, TextClip, ColorClip
from glob import glob


class VideoMaker:

    @staticmethod
    def folder_cleaning(*args) -> None:
        """
        Cleans all the files inside the path that is given.
        :param args: str paths
        """
        for path in args:
            for file in glob(path + "*"):
                os.remove(file)

    @staticmethod
    def folder_scanning(image_path: str, audio_path: str) -> tuple:
        """
        Scans the folder given to the class VideoMaker and sorts them
        :param image_path: a string containing the location of the image
        :param audio_path: a string containing the location of the audio
        :return: tuple of two lists containing img_list and music_list.
        """
        images = [f for f in os.scandir(image_path) if str(f.name).split(".")[0].isdigit() and "." in str(f.name)]
        audios = [f for f in os.scandir(audio_path) if str(f.name).lower().endswith('.wav')]
        images.sort(key=lambda e: int(str(e.name).split('.')[0]))
        audios.sort(key=lambda e: int(str(e.name).split('.')[0]))
        return images, audios

    @staticmethod
    def add_fallbacks(sentences_len: int, images: list) -> list:
        """
        In case there is no image for a specific audio pair a fallback image will be added.
        :param sentences_len: an int mentioning how many images should be
        :param images: DirEntry image file
        :return: the image list with fallback images added.
        """
        fallback_list = []
        e = 0
        for i in range(sentences_len):
            try:
                if int(str(images[e].name).split(".")[0]) != i:
                    fallback_list.insert(i, "fallback.jpg")
                    e -= 1
                else:
                    fallback_list.append(images[e])
            except IndexError:
                fallback_list.insert(i, "fallback.jpg")
            e += 1
        return fallback_list

    @staticmethod
    def images_to_pil(fallback_list: list, resize_size=800):
        """
        Convert images in a list into pil_images
        :param fallback_list:
        :param resize_size:
        :return:
        """
        pil_images = []
        for image in fallback_list:
            try:
                pillow_img = PIL.Image.open(image.path)
            except AttributeError:
                pillow_img = PIL.Image.open(image)
            width, height = pillow_img.size
            if width > resize_size:
                pillow_img = pillow_img.resize((resize_size, pillow_img.size[1]))
            if height > resize_size:
                pillow_img = pillow_img.resize((pillow_img.size[0], resize_size))
            img = np.asarray(pillow_img.convert('RGB'))
            pil_images.append(img)
        return pil_images

    @staticmethod
    def audios_to_afc(audios: list) -> list:
        """
        Convert a list of DirEntries audio  into a list of AudioFileClips
        :param audios: list of DirEntries
        :return: list of AudioFileClips
        """
        afc_list = [mp.AudioFileClip(f.path) for f in audios]
        return afc_list

    @staticmethod
    def make_composite_list(pil_images: list, afc_list: list, sentences_list: list) -> list:
        """
        Create a CompositeVideoClip with subtitles, audio and images
        :param pil_images: list of  PIL.Images
        :param afc_list: list of AudioFileClips
        :param sentences_list: list of strings for subtitles
        :return: list of CompositeVideoClip
        """
        clips_with_audio = []
        for index, pil_image in enumerate(pil_images):
            img_clip = mp.ImageClip(pil_image).set_duration(afc_list[index].duration)
            # Calculate font size based on image width and text length
            sub_height = (len(sentences_list[index]) // 38) * 28 + 28
            txt_clip = TextClip(sentences_list[index], fontsize=26, color='white', stroke_width=3,
                                size=(640, sub_height), method='caption', align='south')
            bg_clip = ColorClip(size=(txt_clip.size[0] + 10, txt_clip.size[1] + 10), color=(0, 0, 0, 128))
            # Position the text at the bottom of the screen.
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(img_clip.duration)
            bg_clip = bg_clip.set_position(('center', 'bottom')).set_duration(img_clip.duration)
            # Overlay the text on the image.
            composite = CompositeVideoClip([img_clip, bg_clip, txt_clip])
            clips_with_audio.append(composite.set_audio(afc_list[index]))
        return clips_with_audio
