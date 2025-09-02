import wave
from piper import PiperVoice
from time import time, sleep
from sounddevice import OutputStream, RawOutputStream
import numpy as np
from queue import Queue
from threading import Thread

class TTSHandler:
    def __init__(self, model_path):
        self.voice = PiperVoice.load(model_path, use_cuda=True)
        self.sample_rate = self.voice.config.sample_rate
        self.audio_queue = Queue()
        self.current_synthesis = None
        self.stream = None
        self.synthesis_thread = None
        self.is_playing = False

    def setup_audio_stream(self):
        def audio_callback(outdata, frames, time, status):
            print(f"Audio callback called with {frames} frames")
            try:
                chunk = self.audio_queue.get_nowait()
                if len(chunk) < frames:
                    padded = np.zeros(frames, dtype=np.int16)
                    padded[:len(chunk)] = chunk
                    outdata[:] = padded.reshape(-1, 1)
                else:
                    print(f"Audio queue has {len(chunk)} frames {frames} requested")
                    outdata[:] = chunk[:frames].reshape(-1, 1)
                self.is_playing = True
            except:
                outdata.fill(0)
                self.is_playing = False

        self.stream = OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            callback=audio_callback,
            blocksize=1024,
            latency='low'
        )
        self.stream.start()

    def cancel_current_audio(self, graceful=True, fade_ms=50):
        """Cancel ongoing synthesis and playback"""
        # Stop synthesis
        if self.synthesis_thread and self.synthesis_thread.is_alive():
            # Signal synthesis to stop (implementation depends on your threading)
            pass

        # Clear audio queue with optional fade
        if graceful and not self.audio_queue.empty():
            try:
                # Apply fade to first remaining chunk
                first_chunk = self.audio_queue.get_nowait()
                fade_samples = int(fade_ms * self.sample_rate / 1000)
                fade_length = min(len(first_chunk), fade_samples)

                if fade_length > 0:
                    fade_curve = np.linspace(1.0, 0.0, fade_length)
                    first_chunk[:fade_length] = (first_chunk[:fade_length] * fade_curve).astype(np.int16)
                    self.audio_queue.put(first_chunk)
            except:
                pass

        # Clear remaining queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break

# https://github.com/rhasspy/piper/discussions/326#discussioncomment-8855827
def main():
    start = time()
    model_path = "en_US-lessac-high.onnx"
    model_path = "en_US-lessac-medium.onnx"
    voice = PiperVoice.load(model_path, use_cuda=True)
    #handler = TTSHandler(model_path)
    #handler.setup_audio_stream()
    print(f"Loaded voice in {time() - start:.2f} seconds")

    dialogue = "All these bright lights and loud noises. I find it all so dreadfully...tedious. Or perhaps you've come to amuse me?"


    """
    start = time()
    for chunk in voice.synthesize(dialogue):
        for x in np.array_split(chunk.audio_int16_array, 1024):
            handler.audio_queue.put(x)
        elapsed = time() - start
        start = time()
        print(f"Synthesized in {elapsed:.2f} seconds")
    """


    """
    with wave.open("test.wav", "wb") as wav_file:
        start = time()
        voice.synthesize_wav(dialogue, wav_file)
        print(f"Synthesized in {time() - start:.2f} seconds")
    """

    stream = OutputStream(samplerate=voice.config.sample_rate, blocksize=1024, channels=1, dtype="int16")
    stream.start()

    def audio_thread(stop: list[bool]):
        start = time()
        latency = None
        for chunk in voice.synthesize(dialogue):
            if latency is None:
                latency = time() - start
                print(f"Latency: {latency:.2f} seconds")

            for x in np.array_split(chunk.audio_int16_array, 1024):
                stream.write(x)
                if stop[0]:
                    print("Stopping!")
                    return

    stop = [False]
    thread = Thread(target=audio_thread, args=(stop,))
    thread.start()

    sleep(1)
    stop[0] = True

    thread.join()



if __name__ == "__main__":
    main()
