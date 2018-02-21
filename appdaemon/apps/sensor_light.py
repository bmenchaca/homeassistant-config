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

class SensorLight(hass.Hass):

    def initialize(self):
    
        self.handle = None
        # Check some Params
        # Subscribe to sensors
        if "sensor" in self.args:
            self.listen_state(self.motion, self.args["sensor"], new="on")
            if "off_delay" in self.args:
                self.listen_state(self.quiesce, self.args["sensor"], new="off",
                        duration = self.args["off_delay"])
            else:
                self.listen_state(self.quiesce, self.args["sensor"], new="off")
        else:
            self.log("No sensor specified, doing nothing")
    
    def motion(self, entity, attribute, old, new, kwargs):
        if "entity_on" in self.args:
            self.log("Motion detected: turning {} on".format(self.args["entity_on"]))
            self.turn_on(self.args["entity_on"])
        else:
            self.log("Motion detected: no 'entity_on' specified, doing nothing.")
  
    def quiesce(self, entity, attribute, old, new, kwargs):
        if "entity_on" in self.args:
            self.log("Motion stopped: turning {} off".format(self.args["entity_on"]))
            self.turn_off(self.args["entity_on"])
        else:
            self.log("Motion stopped: no 'entity_on' specified, doing nothing.")
