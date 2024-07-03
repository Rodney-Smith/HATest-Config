"""Adds config flow for Chime TTS."""
import logging
import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .helpers.helpers import ChimeTTSHelper
from .const import (
    DOMAIN,
    VERSION,
    QUEUE_TIMEOUT_KEY,
    QUEUE_TIMEOUT_DEFAULT,
    TTS_PLATFORM_KEY,
    OFFSET_KEY,
    DEFAULT_OFFSET_MS,
    FADE_TRANSITION_KEY,
    DEFAULT_FADE_TRANSITION_MS,
    MEDIA_DIR_KEY,
    MEDIA_DIR_DEFAULT,
    CUSTOM_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_KEY,
    TEMP_CHIMES_PATH_DEFAULT,
    TEMP_PATH_KEY,
    TEMP_PATH_DEFAULT,
    WWW_PATH_KEY,
    WWW_PATH_DEFAULT,
)

LOGGER = logging.getLogger(__name__)
helpers = ChimeTTSHelper()

@config_entries.HANDLERS.register(DOMAIN)
class ChimeTTSFlowHandler(config_entries.ConfigFlow):
    """Config flow for Chime TTS."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return ChimeTTSOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Chime TTS async_step_user."""
        LOGGER.debug("----- Adding Chime TTS Version %s -----", VERSION)

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        tts_platforms = helpers.get_installed_tts_platforms(self.hass)
        if len(tts_platforms) == 0:
            LOGGER.debug("No TTS Platforms detected")
            return self.async_show_form(
                        step_id="no_tts_platforms",
                        data_schema=None,
                        description_placeholders=user_input,
                        last_step=True
                    )

        return self.async_create_entry(title="Chime TTS", data={})


    async def async_step_no_tts_platforms(self, user_input=None):
        """Warn the user that no TTS platforms are installed."""
        return self.async_create_entry(title="Chime TTS", data={})

class ChimeTTSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow Chime TTS integration."""

    data: dict

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        LOGGER.debug("-----  Chime TTS Version %s Configuration -----", VERSION)
        self.config_entry = config_entry

    async def async_step_init(self, user_input={}):
        """Initialize the options flow."""

        stripped_tts_platforms = self.get_installed_tts()
        default_tts = stripped_tts_platforms[0] if len(stripped_tts_platforms) > 0 else ""
        if self.hass is not None:
            root_path = self.hass.config.path("").replace("/config/", "")
        else:
            LOGGER.warning("Unable to determine root path")
            root_path = ""

        # Fetch entered values
        if user_input is None:
            user_input = {}

        # Installed TTS platforms
        tts_platforms = sorted(helpers.get_installed_tts_platforms(self.hass))

        # Media Folders
        media_dirs = self.hass.config.media_dirs or {}
        default_media_dir = MEDIA_DIR_DEFAULT if (MEDIA_DIR_DEFAULT in media_dirs) else (next(iter(media_dirs)) if media_dirs else "local")
        selected_media_dir = self.get_data_key_value(
                MEDIA_DIR_KEY,
                user_input.get(MEDIA_DIR_KEY, default_media_dir)
        )
        media_dirs_labels = ["local" if default_media_dir else "No media directories available"]
        for key, _value in media_dirs.items():
            if key not in media_dirs_labels:
                media_dirs_labels.append(key)


        self.data = {
            QUEUE_TIMEOUT_KEY: self.get_data_key_value(
                QUEUE_TIMEOUT_KEY,
                user_input.get(QUEUE_TIMEOUT_KEY, QUEUE_TIMEOUT_DEFAULT)),
            TTS_PLATFORM_KEY: self.get_data_key_value(
                TTS_PLATFORM_KEY,
                user_input.get(TTS_PLATFORM_KEY, default_tts)),
            OFFSET_KEY: self.get_data_key_value(
                OFFSET_KEY,
                user_input.get(OFFSET_KEY, DEFAULT_OFFSET_MS)),
            FADE_TRANSITION_KEY: self.get_data_key_value(
                FADE_TRANSITION_KEY,
                user_input.get(FADE_TRANSITION_KEY, DEFAULT_FADE_TRANSITION_MS)),
            MEDIA_DIR_KEY: selected_media_dir,
            CUSTOM_CHIMES_PATH_KEY: user_input.get(
                CUSTOM_CHIMES_PATH_KEY,
                self.get_data_key_value(CUSTOM_CHIMES_PATH_KEY, "")),
            TEMP_CHIMES_PATH_KEY: self.get_data_key_value(
                TEMP_CHIMES_PATH_KEY,
                user_input.get(TEMP_CHIMES_PATH_KEY, f"{root_path}{TEMP_CHIMES_PATH_DEFAULT}")),
            TEMP_PATH_KEY: self.get_data_key_value(
                TEMP_PATH_KEY,
                user_input.get(TEMP_PATH_KEY, f"{root_path}{TEMP_PATH_DEFAULT}")),
            WWW_PATH_KEY: self.get_data_key_value(
                WWW_PATH_KEY,
                user_input.get(WWW_PATH_KEY, f"{root_path}{WWW_PATH_DEFAULT}"))
        }

        options_schema = vol.Schema(
            {
                vol.Required(QUEUE_TIMEOUT_KEY, default=self.data[QUEUE_TIMEOUT_KEY]): int,
                vol.Required(TTS_PLATFORM_KEY, default=self.data[TTS_PLATFORM_KEY]):selector.SelectSelector(
                    selector.SelectSelectorConfig(options=tts_platforms,
                                                  mode=selector.SelectSelectorMode.DROPDOWN,
                                                  custom_value=True),
                    ),
                vol.Optional(OFFSET_KEY, default=self.data[OFFSET_KEY]): int,
                vol.Optional(FADE_TRANSITION_KEY, default=self.data[FADE_TRANSITION_KEY]): int,
                vol.Optional(CUSTOM_CHIMES_PATH_KEY,default=self.data[CUSTOM_CHIMES_PATH_KEY]): str,
                vol.Required(MEDIA_DIR_KEY, default=selected_media_dir):selector.SelectSelector(
                    selector.SelectSelectorConfig(options=media_dirs_labels,
                                                  mode=selector.SelectSelectorMode.DROPDOWN,
                                                  custom_value=True),
                    ),
                vol.Required(TEMP_CHIMES_PATH_KEY,default=self.data[TEMP_CHIMES_PATH_KEY]): str,
                vol.Required(TEMP_PATH_KEY,default=self.data[TEMP_PATH_KEY]): str,
                vol.Required(WWW_PATH_KEY,default=self.data[WWW_PATH_KEY]): str
            }
        )
        # Display the configuration form with the current values
        if user_input == {} or user_input is None:
            user_input = None
            return self.async_show_form(
                step_id="init",
                data_schema=options_schema,
                description_placeholders=user_input,
                last_step=True,
            )

        # Validation

        _errors = {}

        # Timeout
        if user_input[QUEUE_TIMEOUT_KEY] < 0:
            _errors["base"] = "timeout"
            _errors[QUEUE_TIMEOUT_KEY] = "timeout_sub"

        # Default TTS Platform
        if user_input.get(TTS_PLATFORM_KEY, None) and len(user_input[TTS_PLATFORM_KEY]) > 0:

            # Replace friendly name with entity/platform name
            default_tts_provider = helpers.get_stripped_tts_platform(user_input[TTS_PLATFORM_KEY])
            stripped_tts_platforms = [platform.lower().replace("tts", "").replace(" ", "").replace(" ", "").replace(".", "").replace("-", "").replace("_", "") for platform in helpers.get_installed_tts_platforms(self.hass)]
            default_tts_provider = default_tts_provider.lower().replace("tts", "").replace(" ", "").replace(" ", "").replace(" ", "").replace(".", "").replace("-", "").replace("_", "")

            if len(stripped_tts_platforms) == 0:
                _errors[TTS_PLATFORM_KEY] = "default_tts_platform_none"
            elif default_tts_provider not in stripped_tts_platforms:
                LOGGER.debug("Unable to find TTS platform %s", user_input[TTS_PLATFORM_KEY])
                _errors[TTS_PLATFORM_KEY] = "default_tts_platform_select"
            else:
                index = stripped_tts_platforms.index(default_tts_provider)
                default_tts_provider = helpers.get_installed_tts_platforms(self.hass)[index]

            user_input[TTS_PLATFORM_KEY] = default_tts_provider

        # Folder path used for `chime_tts.say_url`
        www_path: str = user_input.get(WWW_PATH_KEY, "")
        if not (www_path.startswith(f"{root_path}/media/") != -1 or
                www_path.startswith(f"{root_path}/config/www/") != -1):
            _errors["www_path"] = "www_path"

        if _errors:
            return self.async_show_form(
                step_id="init", data_schema=options_schema, errors=_errors
            )

        if not user_input.get(CUSTOM_CHIMES_PATH_KEY) or len(user_input.get(CUSTOM_CHIMES_PATH_KEY)) == 0:
            self.data[CUSTOM_CHIMES_PATH_KEY] = ""

        # 1st time Custom Chimes Folder path modified
        if (user_input.get(CUSTOM_CHIMES_PATH_KEY)
            and not self.config_entry.options.get(CUSTOM_CHIMES_PATH_KEY)):
            # Show restart reminder step before saving config
            return self.async_show_form(
                step_id="restart_required",
                    data_schema=None,
                    description_placeholders=user_input,
                    last_step=True
                )

        # User input is valid, update the options
        LOGGER.debug("Updating configuration...")
        return self.async_create_entry(
            data=user_input
        )

    async def async_step_restart_required(self, user_input):
        """Warn the user that Home Assistant needs to be restarted."""
        return self.async_create_entry(
            data=self.data
        )

    def get_data_key_value(self, key, default=None):
        """Get the value for a given key. Options flow 1st, Config flow 2nd."""
        dicts = [dict(self.config_entry.options), dict(self.config_entry.data)]
        for p_dict in dicts:
            if key in p_dict:
                return p_dict[key]
        return default


    async def ping_url(self, url: str):
        """Ping a URL and receive a boolean result."""
        if url is None:
            return False
        try:
            response = await self.hass.async_add_executor_job(requests.head, url)
            if 200 <= response.status_code < 300:
                return True
            LOGGER.warning("Error: Received status code %s from %s", str(response.status_code), url)
        except requests.ConnectionError:
            LOGGER.warning("Error: Failed to connect to %s", url)

        return False

    def get_installed_tts(self):
        """List of installed TTS platforms."""
        return list((self.hass.data["tts_manager"].providers).keys())
