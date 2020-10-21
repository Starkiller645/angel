#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
import requests
import json
import os
import ffmpeg
from angellib.threadsignals import ThreadSignals

class VideoWorker(QRunnable):
    def __init__(self, jsonUrl):
        super(VideoWorker, self).__init__()
        self.signals = ThreadSignals()
        self.jsonUrl = jsonUrl

    @pyqtSlot()
    def run(self):
        if os.name != "posix":
            isWindows = True
        else:
            isWindows = False
        if os.environ.get("DEBUG") == "true":
            debug = True
        else:
            debug = False

        if isWindows:
            jsonFile = open('{}/Angel/temp/vid_json.json'.format(appData), 'wb')
        else:
            jsonFile = open('/opt/angel-reddit/temp/vid_json.json', 'wb')
        initRequest = requests.get(self.jsonUrl)
        request = initRequest.url
        request = request[:len(request) - 1]
        request += '.json'
        print(request)
        finalRequest = requests.get(request, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
        jsonFile.write(finalRequest.content)
        jsonFile.close()
        if isWindows:
            jsonFile = open('{}/Angel/temp/vid_json.json'.format(appData), 'r')
        else:
            jsonFile = open('/opt/angel-reddit/temp/vid_json.json', 'r')
        parsedJson = json.loads(jsonFile.read())
        print(parsedJson[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"])
        rawUrl = parsedJson[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
        audioUrl = rawUrl[:rawUrl.rfind('/')] + '/audio'
        print(audioUrl)
        if isWindows:
            with open('{}/Angel/temp/.vid.mp4'.format(appData), 'wb') as video:
                data = requests.get(rawUrl)
                video.write(data.content)
        else:
            with open('/opt/angel-reddit/temp/.vid.mp4', 'wb') as video:
                data = requests.get(rawUrl)
                video.write(data.content)

        if isWindows:
            # FFmpeg is not easily available on windows, so for now there is no support for sound on this platform
            # In a later release we will add a different audio/video backend that supports windows and is installed
            # from PyPi
            self.videoPath = '{}/Angel/temp/.vid.mp4'.format(appData)
            self.signals.videoPath.emit(self.videoPath)
            self.signals.done.emit()
            self.signals.addVideoWidget.emit(self.videoPath)
        else:
            try:
                with open('/opt/angel-reddit/temp/.aud.mp4', 'wb') as audio:
                    data = requests.get(audioUrl, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
                    audio.write(data.content)
            except:
                with open('/opt/angel-reddit/temp/.aud.mp4', 'wb') as audio:
                    audioUrl = rawUrl[:rawUrl.rfind('/')] + '/DASH_audio.mp4'
                    data = requests.get(audioUrl, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
                    audio.write(data.content)
            audio = open('/opt/angel-reddit/temp/.aud.mp4', 'rt')
            try:
                if '?xml' not in audio.read():
                    video = ffmpeg.input('{}/Angel/temp/.vid.mp4'.format(appData))
                    audio = ffmpeg.input('{}/Angel/temp/.aud.mp4'.format(appData))
                    output = ffmpeg.output(video, audio, '{}/Angel/temp/combined.mp4'.format(appData), vcodec='copy', acodec='aac', strict='experimental')
                    self.videoPath = '{}/Angel/temp/combined.mp4'.format(appData)
                    self.signals.videoPath.emit(self.videoPath)
                    self.signals.done.emit()
                    self.signals.addVideoWidget.emit(self.videoPath)
            except:
                video = ffmpeg.input('{}/Angel/temp/.vid.mp4'.format(appData))
                audio = ffmpeg.input('{}/Angel/temp/.aud.mp4'.format(appData))
                output = ffmpeg.output(video, audio, '{}/Angel/temp/combined.mp4'.format(appData), vcodec='copy', acodec='aac', strict='experimental')
                self.videoPath = '{}/Angel/temp/combined.mp4'.format(appData)
                self.signals.videoPath.emit(self.videoPath)
                self.signals.done.emit()
                self.signals.addVideoWidget.emit(self.videoPath)
            audio = open('/opt/angel-reddit/temp/.aud.mp4', 'rt')
            try:
                if '?xml' in audio.read():
                    if debug:
                        print('[DBG] Error downloading audio for video\n[DBG] Trying again with new URL format')
                    raise OSError
                    pass
                else:
                    audio.close()
                    video = ffmpeg.input('/opt/angel-reddit/temp/.vid.mp4')
                    audio = ffmpeg.input('/opt/angel-reddit/temp/.aud.mp4')
                    output = ffmpeg.output(video, audio, '/opt/angel-reddit/temp/combined.mp4', vcodec='copy', acodec='aac', strict='experimental')
                    output.run(overwrite_output=True)
                    self.videoPath = '/opt/angel-reddit/temp/combined.mp4'
                    self.signals.videoPath.emit(self.videoPath)
                    self.signals.done.emit()
                    self.signals.addVideoWidget.emit(self.videoPath)
            except OSError:
                os.remove('/opt/angel-reddit/temp/.aud.mp4')
                audioUrl = rawUrl[:rawUrl.rfind('/')] + '/DASH_audio.mp4'
                if debug:
                    print('[DBG] Trying with new URL scheme\n{}'.format(audioUrl))
                with open('/opt/angel-reddit/temp/.aud.mp4', 'wb') as audio:
                    data = requests.get(audioUrl, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
                    audio.write(data.content)
                    audio.close()
                    audio = open('/opt/angel-reddit/temp/.aud.mp4', 'rt')
                    try:
                        print(audio.read())
                    except UnicodeDecodeError:
                        requestFailed = False
                    else:
                        requestFailed = True
                    if requestFailed:
                        if debug:
                            print('[DBG] Error downloading audio for video')
                        self.videoPath = '/opt/angel-reddit/temp/.vid.mp4'
                        audio.close()
                        self.signals.videoPath.emit(self.videoPath)
                        self.signals.done.emit()
                        self.signals.addVideoWidget.emit(self.videoPath)
                    else:
                        audio.close()
                        video = ffmpeg.input('/opt/angel-reddit/temp/.vid.mp4')
                        audio = ffmpeg.input('/opt/angel-reddit/temp/.aud.mp4')
                        output = ffmpeg.output(video, audio, '/opt/angel-reddit/temp/combined.mp4', vcodec='copy', acodec='aac', strict='experimental')
                        output.run(overwrite_output=True)
                        self.videoPath = '/opt/angel-reddit/temp/combined.mp4'
                        self.signals.videoPath.emit(self.videoPath)
                        self.signals.done.emit()
                        self.signals.addVideoWidget.emit(self.videoPath)
            else:
                audio.close()
                self.videoPath = '/opt/angel-reddit/temp/.vid.mp4'
                self.signals.self.videoPath.emit(self.videoPath)
                self.signals.done.emit()
                self.signals.addVideoWidget.emit(self.videoPath)
