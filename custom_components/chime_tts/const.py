"""Constants for chime_tts."""
from logging import Logger, getLogger

import os
import json

LOGGER: Logger = getLogger(__package__)

DOMAIN = "chime_tts"
NAME = "Chime TTS"
DESCRIPTION = "A custom Home Assistant integration to play audio with text-to-speech (TTS) messages"

# Get version number from manifest.json
integration_dir = os.path.dirname(__file__)
manifest_path = os.path.join(integration_dir, "manifest.json")
if os.path.isfile(manifest_path):
    with open(manifest_path) as manifest_file:
        manifest_data = json.load(manifest_file)
    VERSION = manifest_data.get("version")
else:
    VERSION = None

SERVICE_SAY = "say"
SERVICE_SAY_URL = "say_url"
SERVICE_CLEAR_CACHE = "clear_cache"
PAUSE_DURATION_MS = 450
DATA_STORAGE_KEY = "chime_tts_integration_data"
AUDIO_PATH_KEY = "audio_path"
AUDIO_DURATION_KEY = "audio_duration"
TEMP_PATH = "/media/sounds/temp/chime_tts/"
MP3_PRESET_PATH = "custom_components/chime_tts/mp3s/"
MP3_PRESET_PATH_PLACEHOLDER = "mp3_path_placeholder-"
QUEUE = "QUEUE"
QUEUE_STATUS = "QUEUE_STATUS"
QUEUE_RUNNING = "QUEUE_RUNNING"
QUEUE_IDLE = "QUEUE_IDLE"
QUEUE_CURRENT_ID = "QUEUE_CURRENT_ID"
QUEUE_LAST_ID = "QUEUE_LAST_ID"
QUEUE_TIMEOUT_S = 20


# TTS Platforms
AMAZON_POLLY = "amazon_polly"
BAIDU = "baidu"
GOOGLE_CLOUD = "google_cloud"
GOOGLE_TRANSLATE = "google_translate"
IBM_WATSON_TTS = "watson_tts"
MARYTTS = "MaryTTS"
MICROSOFT_TTS = "microsoft"
MICROSOFT_EDGE_TTS = "edge_tts"
NABU_CASA_CLOUD_TTS = "cloud"
NABU_CASA_CLOUD_TTS_OLD = "cloud_say"
PICOTTS = "picotts"
PIPER = "tts.piper"
VOICE_RSS = "voicerss"
YANDEX_TTS = "yandextts"
