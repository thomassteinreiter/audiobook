import os

import nltk
from typing import Generator
import requests
from urllib.parse import quote


def lazy_sentence_tokenize(file_path: str) -> Generator[str, None, None]:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        content = content.replace('\r\n', ' ').replace('\n', ' ') # remove line breaks so that the sentence normalization works across lines
        sentences = nltk.sent_tokenize(content)
        for s in sentences:
            yield s


def tts(text: str) -> bytes:
    url = f"http://localhost:5002/api/tts?text={quote(text)}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: Unable to fetch audio data for text '{text}'")
        return b''


if __name__ == '__main__':
    file_path = '/home/user/mytext.txt'
    output_path = '/home/user/output/'
    os.makedirs(output_path, exist_ok=True)

    sentences_generator = lazy_sentence_tokenize(file_path)

    for i, sentence in enumerate(sentences_generator):
        print(f"processing: {sentence}")

        filename = os.path.join(output_path, f"segment_{i:05d}.wav")

        text_wav = tts(sentence)

        if text_wav:
            with open(filename, "wb") as file:
                file.write(text_wav)

    print('Done')
