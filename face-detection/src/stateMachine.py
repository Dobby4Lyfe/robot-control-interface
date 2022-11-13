from state_machine import acts_as_state_machine, before, State, Event, after, InvalidStateTransition
from messaging.telemetry import TelemetryClient

@acts_as_state_machine
class Dobby():
    def __init__(self, telemetryClient: TelemetryClient) -> None:
        self.target_x = None
        self.target_y = None
        self.telemetryClient = telemetryClient

    name = 'Dobby'

    seeking = State(initial=True)
    locked = State()

    lockFace = Event(from_states=seeking, to_state=locked)
    lostFace = Event(from_states=locked, to_state=seeking)

    @before('lockFace')
    def find_target(self):
        self.telemetryClient.debug("Dobby can see you at x:{x} y:{y}, Dobby is excited!".format(
            x=self.target_x, y=self.target_y), "Dobby State")

    @after('lostFace')
    def lose_target(self):
        self.telemetryClient.debug("Dobby can't find you, Dobby is sad", "Dobby State")

    def set_face_location(self, x, y):
        self.target_y = y
        self.target_x = x
        if (self.is_seeking):
            self.lockFace()
   
    def set_no_face(self):
        if (self.is_locked):
            self.lostFace()
