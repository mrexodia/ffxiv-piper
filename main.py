import wave
from piper import PiperVoice
from time import time

def main():
    start = time()
    voice = PiperVoice.load("en_US-lessac-medium.onnx", use_cuda=True)
    print(f"Loaded voice in {time() - start:.2f} seconds")
    with wave.open("test.wav", "wb") as wav_file:
        start = time()
        voice.synthesize_wav("All these bright lights and loud noises. I find it all so dreadfully...tedious. Or perhaps you've come to amuse me?", wav_file)
        print(f"Synthesized in {time() - start:.2f} seconds")

    start = time()
    for chunk in voice.synthesize("All these bright lights and loud noises. I find it all so dreadfully...tedious. Or perhaps you've come to amuse me?"):
        print(f"Synthesized in {time() - start:.2f} seconds")
        print(chunk.sample_rate, chunk.sample_width, chunk.sample_channels)
        break

if __name__ == "__main__":
    main()
