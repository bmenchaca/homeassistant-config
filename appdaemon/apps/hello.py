import appdaemon.plugins.hass.hassapi as hass

class HelloWorld(hass.Hass):

    def initialize(self):
        self.log("Hello from Appdaemon")
        self.log("You are now ready to run apps!")

