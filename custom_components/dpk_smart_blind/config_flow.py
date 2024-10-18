"""Adds config flow for ETO."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)

# https://github.com/home-assistant/core/blob/master/homeassistant/const.py
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import callback

from .const import (
    CONF_SHADED_AREA,
    CONF_WINDOW_HEIGHT,
    CONFIG_FLOW_VERSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class DPKSmartBlindConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for API."""

    VERSION = CONFIG_FLOW_VERSION

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> DPKSmartBlindOptionsFlow:
        """Get the options flow for this handler."""
        return DPKSmartBlindOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Handle initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_WINDOW_HEIGHT): float,
                        vol.Required(CONF_SHADED_AREA): float,
                    }
                ),
            )

        await self.async_set_unique_id(user_input[CONF_NAME].lower())
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=user_input[CONF_NAME],
            data={CONF_NAME: user_input[CONF_NAME]},
            options={**user_input},
        )


class DPKSmartBlindOptionsFlow(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_WINDOW_HEIGHT,
                        default=self.config_entry.options[CONF_WINDOW_HEIGHT],
                    ): vol.Coerce(float),
                    vol.Required(
                        CONF_SHADED_AREA,
                        default=self.config_entry.options[CONF_SHADED_AREA],
                    ): vol.Coerce(float),
                }
            ),
        )
