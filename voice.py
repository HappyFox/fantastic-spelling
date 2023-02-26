import multiprocessing
import time

import pyttsx3


_voice_process = None
_queue = multiprocessing.Queue()


def _process_utterances(queue):
    tts = pyttsx3.init()
    tts.setProperty("rate", 175)

    while True:
        utterance = queue.get()
        if not utterance:
            queue.close()
            return  # queue closed, go home.

        tts.say(utterance)
        tts.runAndWait()


def start():
    global _voice_process
    _voice_process = multiprocessing.Process(target=_process_utterances, args=(_queue,))
    _voice_process.start()


def say(utterance, queue=False):
    if not _queue.empty() and not queue:
        return
    _queue.put_nowait(utterance)


def stop():
    _queue.put(False)
    _voice_process.join()
