# ffxiv-piper

Simple text-to-speech (TTS) server for FFXIV based on [Piper](https://github.com/rhasspy/piper) optimized for low latency. The [FFXIV-TTS](https://github.com/MinhakaDev/FFXIV-TTS) plugin has extremely high latency with the internal voices, so you can configure the websocket instead and use this server.

## Installation

- Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- `uv run python -m piper.download_voices en_US-lessac-medium en_US-danny-low`
- `uv run main.py`

Make sure to configure the FFXIV-TTS plugin to serve on `localhost` port `1567`, otherwise it will not work.

The latency is usually between 200-600ms on my machine (RTX 3090):

```
Raya-O-Senna: Forgive me, John. I would be alone with my thoughts for a while. Worry not: I will find a way to deal with A-Ruhn.
Latency: 0.60 seconds
Raya-O-Senna: Ever does it hearten me to see your face, John. What brings you to the Twelveswood today?
Latency: 0.23 seconds
Raya-O-Senna: Considering the Amdapori horrors that were but recently in our midst, I would say that we fare rather well. The forest once again knows serenity, and we have you to thank for this, John.
```

The history is saved to `history.log`.

## Development

List available voices:

```sh
$ uv run python -m piper.download_voices | rg en_
en_GB-alan-low
en_GB-alan-medium
en_GB-alba-medium
en_GB-aru-medium
en_GB-cori-high
en_GB-cori-medium
en_GB-jenny_dioco-medium
en_GB-northern_english_male-medium
en_GB-semaine-medium
en_GB-southern_english_female-low
en_GB-vctk-medium
en_US-amy-low
en_US-amy-medium
en_US-arctic-medium
en_US-bryce-medium
en_US-danny-low
en_US-hfc_female-medium
en_US-hfc_male-medium
en_US-joe-medium
en_US-john-medium
en_US-kathleen-low
en_US-kristin-medium
en_US-kusal-medium
en_US-l2arctic-medium
en_US-lessac-high
en_US-lessac-low
en_US-lessac-medium
en_US-libritts-high
en_US-libritts_r-medium
en_US-ljspeech-high
en_US-ljspeech-medium
en_US-norman-medium
en_US-reza_ibrahim-medium
en_US-ryan-high
en_US-ryan-low
en_US-ryan-medium
en_US-sam-medium
```
