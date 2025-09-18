import json
import asyncio
from time import time, sleep
from threading import Thread

import numpy as np
from piper import PiperVoice
from sounddevice import OutputStream
from websockets.asyncio.client import connect

class TTS:
    def __init__(self, voice: PiperVoice):
        self.voice = voice
        self.stream = OutputStream(samplerate=voice.config.sample_rate, blocksize=1024, channels=1, dtype="int16")
        self.stream.start()
        self.thread = None
        self.stop = False

    def say(self, text: str):
        def audio_thread():
            start = time()
            latency = None
            for chunk in self.voice.synthesize(text):
                if latency is None:
                    latency = time() - start
                    print(f"Latency: {latency:.2f} seconds")
                for x in np.array_split(chunk.audio_int16_array, self.stream.blocksize):
                    if self.stop:
                        # TODO: fade out instead
                        quiet = np.zeros(self.stream.blocksize, dtype=np.int16)
                        self.stream.write(quiet)
                        return
                    self.stream.write(x)
            self.thread = None

        self.cancel()
        self.thread = Thread(target=audio_thread)
        self.thread.start()

    def cancel(self):
        if self.thread is None:
            return False

        self.stop = True
        self.thread.join()
        self.thread = None
        self.stop = False
        return True

async def main():
    start = time()
    male_voice = PiperVoice.load("en_US-danny-low.onnx", use_cuda=True)
    female_voice = PiperVoice.load("en_US-lessac-medium.onnx", use_cuda=True)
    print(f"Loaded voices in {time() - start:.2f} seconds")

    tts_male = TTS(male_voice)
    tts_female = TTS(female_voice)

    # Append JSON messages to a file with the datetime
    with open("history.log", "a", encoding="utf-8", buffering=1) as log:
        while True:
            try:
                async with connect("ws://localhost:1567/Messages") as ws:
                    while True:
                        text = await ws.recv(decode=True)
                        log.write(f"{time()} {text}\n")
                        message = json.loads(text)
                        match message["Type"]:
                            case "Cancel":
                                f = tts_female.cancel()
                                m = tts_male.cancel()
                                if f or m:
                                    print("[cancel]")
                            case "Say":
                                speaker = message["Speaker"]
                                if not speaker:
                                    speaker = "Announcement"
                                npc_id = message["NpcId"]
                                race = message["Race"]
                                body_type = message["BodyType"]
                                gender = message["Gender"]
                                payload = message["Payload"]
                                print(f"[{npc_id}] {speaker}: {payload}")
                                # Clean up the payload for improved TTS flow
                                payload = payload.replace(" - ", ": ").replace("...", ", ")
                                if gender == "Female":
                                    tts_male.cancel()
                                    tts_female.say(payload)
                                else:
                                    tts_female.cancel()
                                    tts_male.say(payload)
                            case _:
                                print(f"Unknown message: {message}")
            except ConnectionError as e:
                print(f"Error: {e}")
            sleep(1.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
