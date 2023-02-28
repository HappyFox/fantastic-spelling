import asyncio
import multiprocessing
import time

import pyttsx3


_voice_process = None
_queue = multiprocessing.Queue()
_running_event = multiprocessing.Event()


def _process_utterances(queue, running_event):
    tts = pyttsx3.init()
    tts.setProperty("rate", 175)

    while True:
        if queue.empty():
            running_event.clear()
        utterance = queue.get()
        if not utterance:
            queue.close()
            return  # queue closed, go home.

        running_event.set()
        tts.say(utterance)
        tts.runAndWait()


def start():
    global _voice_process
    _voice_process = multiprocessing.Process(
        target=_process_utterances, args=(_queue, _running_event)
    )
    _voice_process.start()


def is_busy():
    return _running_event.is_set()


async def speech_finished():
    await asyncio.sleep(0.1)
    while is_busy():
        await asyncio.sleep(0.1)


def say(utterance, queue=False):
    if _running_event.is_set() and not queue:
        return
    _queue.put_nowait(utterance)


def stop():
    _queue.put(False)
    _voice_process.join()
