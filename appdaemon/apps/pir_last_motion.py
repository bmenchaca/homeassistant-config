import appdaemon.plugins.hass.hassapi as hass

#
# App to watch which binary_sensor in a group changed last, and record it's name as an input_text
# and the datetime as in input_datetime
#
# Args:
#
# input_sensors: binary_sensor(s) to use as trigger
# output_sensor: The sensor that will be updated with the last motion data.
# output_friendly: Friendly name for output sensor
#

class PirLastMotion(hass.Hass):

    def initialize(self):
        self.handle = None
        # Check some Params
        # Subscribe to sensors
        if "input_sensors" in self.args:
            for sensor in self.args["input_sensors"]:
                self.listen_state(self.motion, sensor, new="on")
                self.listen_state(self.quiesce, sensor, new="off")
                self.log("Registering on and off listener for %s motion" % sensor)
        else:
            self.log("No PIR sensors specified, doing nothing")
    

    def motion(self, entity, attribute, old, new, kwargs):
        #self.set_state(self.args["output_sensor"], state = entity.name, attributes = { "friendly_name": self.args["output_friendly"] }
  

    def quiesce(self, entity, attribute, old, new, kwargs):
        self.set_state(self.args["output_sensor"], state = entity.name, attributes = { "friendly_name": self.args["output_friendly"] }
