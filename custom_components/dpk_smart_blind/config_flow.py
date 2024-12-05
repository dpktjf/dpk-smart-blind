"""Adds config flow for ETO."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)

# https://github.com/home-assistant/core/blob/master/homeassistant/const.py
from homeassistant.const import CONF_NAME, DEGREE, PERCENTAGE, UnitOfLength, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    _LOGGER,
    CONF_AZIMUTH,
    CONF_DEFAULT_HEIGHT,
    CONF_DELTA_POSITION,
    CONF_DELTA_TIME,
    CONF_DISTANCE,
    CONF_ENTITY,
    CONF_FOV_LEFT,
    CONF_FOV_RIGHT,
    CONF_HEIGHT_WIN,
    CONF_WEATHER_ENTITY,
    CONF_WEATHER_STATE,
    CONFIG_FLOW_VERSION,
    DOMAIN,
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
    }
)


OPTIONS = vol.Schema(
    {
        vol.Required(CONF_AZIMUTH, default=180): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=359,
                mode=selector.NumberSelectorMode.SLIDER,
                unit_of_measurement=DEGREE,
            )
        ),
        vol.Required(CONF_FOV_LEFT, default=90): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=90,
                step=1,
                mode=selector.NumberSelectorMode.SLIDER,
                unit_of_measurement=DEGREE,
            )
        ),
        vol.Required(CONF_FOV_RIGHT, default=90): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=90,
                step=1,
                mode=selector.NumberSelectorMode.SLIDER,
                unit_of_measurement=DEGREE,
            )
        ),
    }
)

WINDOW_OPTIONS = vol.Schema(
    {
        vol.Required(CONF_ENTITY, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(
                multiple=False,
                filter=selector.EntityFilterSelectorConfig(
                    domain="cover",
                    supported_features=["cover.CoverEntityFeature.SET_POSITION"],
                ),
            )
        ),
        vol.Required(CONF_HEIGHT_WIN, default=2.1): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.1,
                max=6,
                step=0.01,
                mode=selector.NumberSelectorMode.SLIDER,
                unit_of_measurement=UnitOfLength.METERS,
            )
        ),
        vol.Required(CONF_DISTANCE, default=0.5): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.1,
                max=2,
                step=0.1,
                mode=selector.NumberSelectorMode.SLIDER,
                unit_of_measurement=UnitOfLength.METERS,
            )
        ),
        vol.Required(CONF_DEFAULT_HEIGHT, default=100): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=100,
                step=1,
                mode=selector.NumberSelectorMode.SLIDER,
                unit_of_measurement=PERCENTAGE,
            )
        ),
    }
).extend(OPTIONS.schema)

CLIMATE_OPTIONS = vol.Schema(
    {
        vol.Required(
            CONF_WEATHER_ENTITY, default=vol.UNDEFINED
        ): selector.EntitySelector(
            selector.EntityFilterSelectorConfig(domain="weather")
        ),
        vol.Required(
            CONF_WEATHER_STATE, default=["sunny", "partlycloudy", "cloudy", "clear"]
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                multiple=True,
                sort=False,
                options=[
                    "clear-night",
                    "clear",
                    "cloudy",
                    "fog",
                    "hail",
                    "lightning",
                    "lightning-rainy",
                    "partlycloudy",
                    "pouring",
                    "rainy",
                    "snowy",
                    "snowy-rainy",
                    "sunny",
                    "windy",
                    "windy-variant",
                    "exceptional",
                ],
            )
        ),
    }
)

AUTOMATION_OPTIONS = vol.Schema(
    {
        vol.Required(CONF_DELTA_POSITION, default=5): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=90,
                step=1,
                mode=selector.NumberSelectorMode.SLIDER,
                unit_of_measurement=PERCENTAGE,
            )
        ),
        vol.Required(CONF_DELTA_TIME, default=2): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement=UnitOfTime.MINUTES,
            )
        ),
    }
)


@callback
def configured_instances(hass: HomeAssistant) -> set[str | None]:
    """Return a set of configured instances."""
    """Should really be unique on the blinds entity within - TODO???"""
    entries = [
        entry.data.get(CONF_NAME) for entry in hass.config_entries.async_entries(DOMAIN)
    ]
    return set(entries)


class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = CONFIG_FLOW_VERSION

    def __init__(self) -> None:
        """Init method."""
        super().__init__()
        self.config: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Handle initial step."""
        if user_input:
            self.config = user_input
            if user_input[CONF_NAME] in configured_instances(self.hass):
                """
                Should really be unique on the blinds entity within - to check.
                If so then replay the user step, rather than moving to the next.
                """
                errors = {}
                errors[CONF_NAME] = "already_configured"
                return self.async_show_form(
                    step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
                )

            return await self.async_step_window()
        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)

    async def async_step_window(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show basic config for window with vertical blind."""
        if user_input is not None:
            self.config.update(user_input)
            return await self.async_step_climate()

        return self.async_show_form(
            step_id="window",
            data_schema=WINDOW_OPTIONS,
        )

    async def async_step_climate(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage climate options."""
        if user_input is not None:
            self.config.update(user_input)
            return await self.async_step_automation()
        return self.async_show_form(step_id="climate", data_schema=CLIMATE_OPTIONS)

    async def async_step_automation(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage automation options."""
        if user_input is not None:
            self.config.update(user_input)
            return await self.async_step_update()
        return self.async_show_form(
            step_id="automation", data_schema=AUTOMATION_OPTIONS
        )

    async def async_step_update(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Create entry."""
        return self.async_create_entry(
            title=self.config[CONF_NAME],
            data={
                CONF_NAME: self.config[CONF_NAME],
            },
            options={
                CONF_AZIMUTH: self.config.get(CONF_AZIMUTH),
                CONF_DEFAULT_HEIGHT: self.config.get(CONF_DEFAULT_HEIGHT),
                CONF_DELTA_POSITION: self.config.get(CONF_DELTA_POSITION),
                CONF_DELTA_TIME: self.config.get(CONF_DELTA_TIME),
                CONF_DISTANCE: self.config.get(CONF_DISTANCE),
                CONF_ENTITY: self.config.get(CONF_ENTITY),
                CONF_FOV_LEFT: self.config.get(CONF_FOV_LEFT),
                CONF_FOV_RIGHT: self.config.get(CONF_FOV_RIGHT),
                CONF_HEIGHT_WIN: self.config.get(CONF_HEIGHT_WIN),
                CONF_WEATHER_ENTITY: self.config.get(CONF_WEATHER_ENTITY),
                CONF_WEATHER_STATE: self.config.get(CONF_WEATHER_STATE),
            },
        )


class OptionsFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.current_config: dict = dict(config_entry.data)
        self.options = dict(config_entry.options)
        _LOGGER.debug("options=%s", self.options)

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Manage the options."""
        options = ["blind", "climate", "automation"]
        """
        if self.options[CONF_CLIMATE_MODE]:
            options.append("climate")
        if self.options.get(CONF_WEATHER_ENTITY):
            options.append("weather")
        if self.options.get(CONF_ENABLE_BLIND_SPOT):
            options.append("blind_spot")
        if self.options.get(CONF_INTERP):
            options.append("interp")
        """
        return self.async_show_menu(step_id="init", menu_options=options)

    async def async_step_blind(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Adjust blind parameters."""
        return await self.async_step_window()

    async def async_step_window(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show basic config for a window with vertical blinds."""
        schema = WINDOW_OPTIONS
        if user_input is not None:
            self.options.update(user_input)
            return await self.async_step_climate()
        return self.async_show_form(
            step_id="window",
            data_schema=self.add_suggested_values_to_schema(
                schema, user_input or self.options
            ),
        )

    async def async_step_climate(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage climate options."""
        if user_input is not None:
            entities = [
                CONF_WEATHER_ENTITY,
            ]
            self.optional_entities(entities, user_input)
            self.options.update(user_input)
            return await self.async_step_automation()
        return self.async_show_form(
            step_id="climate",
            data_schema=self.add_suggested_values_to_schema(
                CLIMATE_OPTIONS, user_input or self.options
            ),
        )

    async def async_step_automation(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage automation options."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()
        return self.async_show_form(
            step_id="automation",
            data_schema=self.add_suggested_values_to_schema(
                AUTOMATION_OPTIONS, user_input or self.options
            ),
        )

    async def _update_options(self) -> ConfigFlowResult:
        """Update config entry options."""
        return self.async_create_entry(title="", data=self.options)

    def optional_entities(
        self, keys: list, user_input: dict[str, Any] | None = None
    ) -> None:
        """Set value to None if key does not exist."""
        for key in keys:
            if key not in user_input:
                user_input[key] = None  # type: ignore  # noqa: PGH003
