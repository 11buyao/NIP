# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : voice_module.py
# Author: TheWu
# Date  : 2020/4/15

"""

"""
import math

import os

import pyttsx3
from mutagen.mp3 import MP3
from aip import AipSpeech

from NIP.settings.settings import BASE_DIR
from . import baidu_api
from pygame import mixer


class VoiceToWord:
    def __init__(self):
        self.rate = 150
        self.volumn = 1.0
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'zh')

    def say_words(self, words):
        self.engine.say(words)

        self.engine.runAndWait()


class BaiduVoiceToWord:
    def __init__(self):
        APP_ID = baidu_api.VOICE_APP_ID
        API_KEY = baidu_api.VOICE_API_KEY
        SECRET_KEY = baidu_api.VOICE_SECRET_KEY

        self.client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        self.file_dir = BASE_DIR + '/utils/voice'
        self.mixer = mixer
        if not self.mixer.get_init():
            self.mixer.init()

    def words_process(self, words):
        words_count = math.ceil(len(words) / 500)
        words_list = []
        for i in range(words_count):
            words_list.append(words[0 + i * 500:500 + i * 500])
        return words_list

    def get_words(self, words, vol=5, pit=5, per=4, spd=5):
        word_list = self.words_process(words)
        for index, value in enumerate(word_list):
            result = self.client.synthesis(value, options={
                'vol': vol,
                'spd': spd,
                'per': per,
                'pit': pit
            })

            if not isinstance(result, dict):
                with open(self.file_dir + '/{}.mp3'.format(index), 'wb') as f:
                    f.write(result)
            else:
                return result

    def merge(self, words):
        with open(self.file_dir + '/voice.mp3', 'wb') as f:
            for i in range(math.ceil(len(words) / 500)):
                with open(self.file_dir + '/{}.mp3'.format(i), 'rb') as f1:
                    f.write(f1.read())
                    os.unlink(self.file_dir + '/{}.mp3'.format(i))
            f.flush()
        audio = MP3(self.file_dir + '/voice.mp3')
        return audio.info.length

    def say_words(self, words, vol=5, pit=5, per=4, spd=5):
        result = self.get_words(words, vol, pit, per, spd)
        if isinstance(result, dict):
            return {'data': '播放错误'}
        else:
            song_length = math.ceil(self.merge(words))
            self.mixer.music.load(self.file_dir + '/voice.mp3')
            self.mixer.music.play()
        return {'song_length': song_length}

    def stop(self):
        self.mixer.music.stop()
        self.mixer.music.fadeout(1)
        return {'song_length': 0}
