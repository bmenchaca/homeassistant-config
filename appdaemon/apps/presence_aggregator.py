import appdaemon.plugins.hass.hassapi as hass

class PresenceAggregator(hass.Hass):
    """App to determine current presence for a person.

 Args:
    trackers: List of device_trackers to use to determine presence.  Each should use a unique method of tracking.
    presence_select: The input_select object to change when home
    home_consensus[optional]: Number of trackers that must agree before we switch from away to home.  Defaults to 1.
    away_consensus[optional]: Number of trackers that must agree before we switch from home to away.  Defaults to all.
    home_delay[optional]: Amount of time to delay before someone is listed as home.  No delay is the default.
    away_delay[optional]: Amount of time to delay before someone is listed as not home.  No delay is the default.
    home_state[optional]: The "Home" state to select when we are home (defaults to "Home")
    away_state[optional]: The "Away" state to select when we are away (defaults to "Away")

    Release Notes

    Version 1.0:
        Initial Version
    """
    def initialize(self):
        self.log("Starting Presence Aggregator.")
        self.home_delay_timer = None
        self.away_delay_timer = None
        self.home_count = 0
        self.away_count = 0
        # Check required Params
        if not "trackers" in self.args or not self.args["trackers"]:
            self.error("No tracker(s) specified, doing nothing.")
            return
        # Also check if each one is a device_tracker object?
        if not "presence_select" in self.args:
            self.error("No input_select specified to change, doing nothing.")
            return
        # Handle optional/defaulted params
        if not "home_consensus" in self.args:
            self.args["home_concensus"] = 1
        if not "away_consensus" in self.args:
            self.args["away_concensus"] = len(self.args["trackers"])
        if not "home_state" in self.args:
            self.args["home_state"] = "Home"
        if not "away_state" in self.args:
            self.args["away_state"] = "Away"
        
        self.log("Number of trackers: %s" % len(self.args["trackers"]))
        # Subscribe to trackers
        for tracker in self.args["trackers"]:
            # Listen for trackers arriving home 
            self.log("Registering a Home arrival tracker for %s." % tracker)
            self.listen_state(self.tracker_is_home, tracker, new='Home')
            # Listen for trackers leaving home
            self.log("Registering a Home departure tracker for %s." % tracker)
            self.listen_state(self.tracker_is_away, tracker, old='Home')
            cur_state = self.get_state(entity = tracker, attribute = "state")
            self.log("Current state of %s is %s." % (tracker, cur_state))
            if cur_state == 'home':
                self.home_count += 1
            else:
                self.away_count += 1
        
        self.log("Away count is %d, Home count is %d." % (self.away_count, self.home_count))


    def tracker_is_home(self, entity, attribute, old, new, kwargs):
        # If the old state was previously home as well, we should do nothing
        if old == "Home":
            return
        # Change the away/home balance
        self.away_count -= 1
        self.home_count += 1
        self.log("Tracker %s is now at Home, away count is %d, home count is %d." %
                 (entity, self.away_count, self.home_count), level = "TRACE")
        # If are below the concensus for away, and we were running an away timer, cancel it
        if self.away_count < self.args["away_concensus"] and self.away_delay_timer:
            self.cancel_timer(self.away_delay_timer)
            self.away_delay_timer = None
            self.log("Dropped below Away Concensus %d < %d, cancelling timer." %
                     (self.away_count, self.args["away_concensus"]), level = "TRACE")
        # If we are now above the concensus for home...
        if self.home_count >= self.args["home_concensus"]:
            # If we above concensus and not on a delay, change now        
            if not self.args["home_delay"]: 
                self.args["presence_select"] = self.args["home_state"]
            # If we are on a delay and don't have a timer, start one
            elif not self.home_delay_timer:
                self.home_delay_timer = self.run_in(home_concensus_delay_callback, self.args["home_delay"])
  

    def tracker_is_away(self, entity, attribute, old, new, kwargs):
        # If the new state is home as well, we should do nothing
        if new == "Home":
            return
        # Change the away/home balance
        self.away_count += 1
        self.home_count -= 1
        self.log("Tracker %s is now not at Home, away count is %d, home count is %d." %
                 (entity, self.away_count, self.home_count), level = "TRACE")
        # If are below the concensus for away, and we were running an away timer, cancel it
        if self.home_count < self.args["home_concensus"] and self.home_delay_timer:
            self.cancel_timer(self.home_delay_timer)
            self.home_delay_timer = None
            self.log("Dropped below Home Concensus %d < %d, cancelling timer." %
                     (self.home_count, self.args["home_concensus"]), level = "TRACE")
        # If we are now above the concensus for away...
        if self.away_count >= self.args["away_concensus"]:
            # If we above concensus and not on a delay, change now        
            if not self.args["away_delay"]: 
                self.args["presence_select"] = self.args["away_state"]
            # If we are on a delay and don't have a timer, start one
            elif not self.away_delay_timer:
                self.away_delay_timer = self.run_in(away_concensus_delay_callback, self.args["away_delay"])


    def home_concensus_delay_callback(self, kwargs):
        self.home_delay_timer = None
        if self.home_count >= self.args["home_concensus"]:
            self.args["presence_select"] = self.args["home_state"]



    def away_concensus_delay_callback(self, kwargs):
        self.away_delay_timer = None
        if self.away_count >= self.args["away_concensus"]:
            self.args["presence_select"] = self.args["away_state"]

