import appdaemon.plugins.hass.hassapi as hass

#
# App to turn lights on when motion detected then off again after a delay
#
# Use with constrints to activate only for the hours of darkness
#
# Args:
#
# sensor: binary sensor to use as trigger
# entity_on : entity to turn on when detecting motion, can be a light, script, scene or anything else that can be turned on
# entity_off : entity to turn off when detecting motion, can be a light, script or anything else that can be turned off. Can also be a scene which will be turned on
# delay: amount of time after turning on to turn off again. If not specified defaults to 60 seconds.
#
# Release Notes
#
# Version 1.1:
#   Add ability for other apps to cancel the timer
#
# Version 1.0:
#   Initial Version

class DayNight(hass.Hass):

    def initialize(self):
        self.handle = None
        # Check some Params
        # Subscribe
        if "entity_day" in self.args:
            if "sunrise_offset" in self.args:
                self.run_at_sunrise(self.sunrise, offset=self.args["sunrise_offset"])
            else:
                self.run_at_sunrise(self.sunrise)
        if "entity_night" in self.args:
            if "sunset_offset" in self.args:
                self.run_at_sunrise(self.sunrise, offset=self.args["sunset_offset"])
            else:
                self.run_at_sunrise(self.sunrise)
    

    def sunrise(self, entity, attribute, old, new, kwargs):
        self.turn_on(self.args["entity_day"])
  

    def sunset(self, entity, attribute, old, new, kwargs):
        self.turn_on(self.args["entity_night"])
