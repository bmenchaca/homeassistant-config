"""
Support for the Proximity Events platform (http://proximityevents.com).

JSON Webhook fields (from http://proximityevents.com/faq/index.html):
trigger_id = Unique UUID representing the trigger
trigger_type = Description of the trigger type. (“Geofence”, “Beacon”, “Visit”,
	or “Location”)
trigger_name = The name used to describe the Trigger. Based on user inputed name
	for Geofences and Beacons and hard coded to "New Location Visits” for
	Visits and "New Location Updates” for Location Triggers
event_id = Unique UUID representing the event
event_type = Combined description of Trigger Type and Event Type separated by a
	“:" (“Geofence:Enter”, "Geofence:Exit”, “Beacon:Enter”, “Beacon:Exit”,
	“Visit:Enter”, “Visit:Exit”, Location:Update”)
event_date = ISO8601 String representation of the date and time the event
	triggered
event_latitude = String with the Latitude value for where the event triggered
event_longitude = String with the Longitude value for where the event triggered
event_accuracy_m = String with the reported value of the accuracy of the event
	location in meters
event_address = String represented a geocoded address associated with the event
	location, if available
event_enter_date = ISO8601 String representation of the arrival date and time
	(Only used for Visit Triggers)
event_exit_date = ISO8601 String representation of the departure date and time
	(Only used for Visit Triggers)

"""
import asyncio
from functools import partial
import logging

import voluptuous as vol

from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.components.http import HomeAssistantView
from homeassistant.const import (
    ATTR_LATITUDE, ATTR_LONGITUDE, HTTP_UNPROCESSABLE_ENTITY, STATE_NOT_HOME)
import homeassistant.helpers.config_validation as cv
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['http']
BEACON_DEV_PREFIX = 'beacon'


ATTR_EVENT_LATITUDE = 'event_latitude'
ATTR_EVENT_LONGITUDE = 'event_longitude'
ATTR_EVENT_ACCURACY = 'event_accuracy_m'
LOCATION_ATTRS = [ ATTR_EVENT_LATITUDE, ATTR_EVENT_LONGITUDE,
                   ATTR_EVENT_ACCURACY ]

ATTR_EVENT_ADDRESS = 'event_address'

GEOFENCE_ENTER = 'Geofence:Enter'
GEOFENCE_EXIT = 'Geofence:Exit'
BEACON_ENTER = 'Beacon:Enter'
BEACON_EXIT = 'Beacon:Exit'

URL = '/api/proximity_events'

def setup_scanner(hass, config, see, discovery_info=None):
    """Set up an endpoint for the Geofency application."""
    hass.http.register_view(ProximityEventsView(see))

    return True


class ProximityEventsView(HomeAssistantView):
    """View to handle Proximity Events requests."""

    url = URL
    name = 'api:proximity_events'

    def __init__(self, see):
        """Initialize Proximity Events url endpoints."""
        self.see = see

    @asyncio.coroutine
    def post(self, request):
        """Handle Proximity Events requests."""
        data = yield from request.json()
        hass = request.app['hass']

        data = self._validate_data(data)
        if not data:
            return ("Invalid data", HTTP_UNPROCESSABLE_ENTITY)

        if data['event_type'] in [ GEOFENCE_ENTER, BEACON_ENTER ]: 
            location_name = data['trigger_name']
        else:
            location_name = STATE_NOT_HOME
        if ATTR_EVENT_LATITUDE in data:
            data[ATTR_LATITUDE] = data[ATTR_EVENT_LATITUDE]
            data[ATTR_LONGITUDE] = data[ATTR_EVENT_LONGITUDE]

        return (yield from self._set_location(hass, data, location_name))

    @staticmethod
    def _validate_data(data):
        """Validate POST payload."""
        data = data.copy()

        required_attributes = [ 'trigger_type', 'trigger_name',
                                'event_type', 'event_date' ]

        valid = True
        for attribute in required_attributes:
            if attribute not in data:
                valid = False
                _LOGGER.error("'%s' not specified in message", attribute)

        if data['trigger_type'] not in [ "Geofence", "Beacon" ]:
            value = False
            _LOGGER.debug("%s is not a supported trigger", data['trigger_type'])

        if not valid:
            _LOGGER.debug(data)
            return False

        data['trigger_name'] = slugify(data['trigger_name'])
        
        if 'event_address' in data:
            data['event_address'] = data['event_address'].replace('\n', ' ')

        for attribute in LOCATION_ATTRS:
            if attribute in data:
                data[attribute] = float(data[attribute])

        return data

    @staticmethod
    def _device_name(data):
        """Return name of device tracker."""
        return "%s_%s" % (data['trigger_type'], data['trigger_name'])

    @asyncio.coroutine
    def _set_location(self, hass, data, location_name):
        """Fire HA event to set location."""
        device = self._device_name(data)
        
        yield from hass.async_add_job(
            partial(self.see, dev_id=device,
                    gps=(data[ATTR_LATITUDE], data[ATTR_LONGITUDE]),
                    location_name=location_name,
                    attributes=data))

        return "Setting location for {}".format(device)
