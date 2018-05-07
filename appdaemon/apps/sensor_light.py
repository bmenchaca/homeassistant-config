import appdaemon.plugins.hass.hassapi as hass

#
# App to turn something on when a sensor is activatedm then off again after a
# delay
#
# Use with constrints to activate only for the hours of darkness
#
# Args:
#
# sensor: binary sensor to use as trigger
# entity_on : entity to turn on when sensor is detected, can be a light, script, scene or anything else that can be turned on
# entity_on_state[optional]: Sensor state that represents activation
# entity_off : entity to turn off when sensor is quieced, can be a light, script or anything else that can be turned off. Can also be a scene which will be turned on
# entity_off_state[optional]: Sensor state that represents deactivation
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
            if "entity_on" in self.args:
                if "entity_on_state" in self.args:
                    entity_on_state = self.args["entity_on_state"]
                else:
                    entity_on_state = "on"
                self.log("Registering 'on' listener for %s, activates %s"
                        % (self.args["sensor"], self.args["entity_on"]))
                self.listen_state(self.activated, self.args["sensor"],
                                  new=entity_on_state)
            if "entity_off" in self.args:
                if "entity_off_state" in self.args:
                    entity_off_state = self.args["entity_on_state"]
                else:
                    entity_off_state = "off"
                if "off_delay" in self.args:
                    self.log("Registering %s listener for %s quiesce, deactivates %s after %d seconds." % (entity_off_state, self.args["sensor"],
                           self.args["entity_off"], self.args["off_delay"]))
                    self.listen_state(self.quiesce, self.args["sensor"],
                                      new=entity_off_state,
                                      duration = self.args["off_delay"])
                else:
                    self.log("Registering %s listener for %s quiesce, deactivates %s immediately." % (entity_off_state, self.args["sensor"],
                      self.args["entity_off"]))
                    self.listen_state(self.quiesce, self.args["sensor"],
                                      new=entity_off_state)
        else:
            self.log("No sensor specified, doing nothing")
    

    def activated(self, entity, attribute, old, new, kwargs):
        #self.log("Motion detected: turning {} on".format(self.args["entity_on"]))
        self.turn_on(self.args["entity_on"])
  

    def quiesce(self, entity, attribute, old, new, kwargs):
        #self.log("Motion stopped: turning {} off".format(self.args["entity_off"]))
        self.turn_off(self.args["entity_off"])
