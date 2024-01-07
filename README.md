# Create your own audiobook with open source tools

## Introduction

This is a proof of concept for creating an audio book using free TTS tools. Starting with a long text file (e.g. extracted from a PDF, copied from the Internet), we can generate an audio file (e.g. MP3, ACC, ...).


## Technologies

I have found that the text-to-speech (TTS) programs on Linux, such as accessibility tools, produce a quality of speech synthesis that, let's say, isn't acceptable for me to listen to for hours on end.

I came across https://github.com/coqui-ai/TTS which produces much better sounding audio.

There is a docker image to get you started: https://github.com/coqui-ai/TTS#docker-image


## Initial experimentation:

```
# start docker container
sudo docker run -it -p 5002:5002 --entrypoint /bin/bash ghcr.io/coqui-ai/tts-cpu

# (inside the container) start the server with a voice model:
python3 TTS/server/server.py --model_name tts_models/en/ljspeech/tacotron2-DDC
```

This launches a web server at http://localhost/5002 where you can enter text and listen to the generated voice.

I quickly found that there are several limitations to the length of text that can be processed at one time. One is the fact that it uses a URL query parameter to post the text, the other limitation is that the speech model can become unstable with longer inputs.

To get around this, I tried to break up my text into smaller parts. The natural "parts" of a text would be the sentences.


## Python script to process larger text

[python/main.py](python/main.py)

Here is a summary of what this Python script does:

1. read a text file
2. remove line breaks (to improve sentence tokenisation)
3. split the text into sentences using https://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.sent_tokenize
4. make an HTTP request to the running coqui-ai docker container
5. store the resulting WAV file in the response in the file system

To listen to the audio, you can enqueue some WAV files into a playlist in a player such as VLC.

Performance: With my old 4-core CPU, it was able to generate about 25 seconds of speech output within 10 seconds.


## Combining the WAV files

I tried assembling the separate WAVs in the Python script, using https://github.com/MaxStrange/AudioSegment, but this failed with some weird array size errors. I did not investigate further and decided to use the command line tool `sox` (Sound eXchange) instead:

```
sox segment_00001.wav segment_00002.wav final.wav
```

Then use ffmpeg to compress it into an ACC file, for example:

```
ffmpeg -i final.wav -c:a aac -b:a 64k -threads 4 final.aac
```

## Findings

1. The most important factor in quality is the input text. For example, if it is a scanned PDF that has been OCRed, structures in the text such as page numbers, images, footnotes, etc. will disrupt the reading flow.
2. Sometimes the TTS model gets "stuck in a loop" where instead of a normal voice you hear a robotic sound that lasts for a few seconds. For me, this happened randomly every 5-10 minutes. It is a bit annoying.
3. Rarely, the HTTP request got stuck completely. It seems to me that certain senctences reliably trigger the problem. I have not been able to find out what exactly is causing this. I suspect it might be something with different quoting styles used in a longer sentence. This happened 3 times in a text input with 10,000 sentences. As the Python script has no good timeout or error handling in general, I killed the script and removed the offending sentence manually.

## Summary

If you have some longer texts/books that you've always wanted to read, but haven't had the time;
If you are not afraid of Linux command tools like docker and like to play a bit with Python;
you can relatively easily produce an audio file with an artificial voice that actually sounds good.
