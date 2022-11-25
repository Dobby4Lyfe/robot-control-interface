from ast import Dict
import time
from state_machine import acts_as_state_machine, before, State, Event, after, InvalidStateTransition
from messaging.contracts import gestureRequestMessage
from messaging.telemetry import TelemetryClient

@acts_as_state_machine
class Dobby():
    def __init__(self, telemetry: TelemetryClient) -> None:
        self.target_x = None
        self.target_y = None
        self.telemetryClient = telemetry

    name = 'Dobby'

    seeking = State(initial=True)
    locked = State()
    gesturing = State()

    lockFace = Event(from_states=seeking, to_state=locked)
    lostFace = Event(from_states=[gesturing,locked], to_state=seeking)
    startGesture = Event(from_states=[seeking,locked], to_state=gesturing)
    
    @before('lockFace')
    def find_target(self):
        self.telemetryClient.debug(f'Dobby can see you at x:{self.target_x} y:{self.target_y}, Dobby is excited!', "Dobby State")

    @after('lostFace')
    def lose_target(self):
        self.telemetryClient.debug("Dobby can't find you, Dobby is sad", "Dobby State")

    @before('startGesture')
    def starting_gesture(self):
        self.telemetryClient.debug("Dobby is performing a gesture!")

    @after('startGesture')
    def finishing_gesture(self):
        self.telemetryClient.debug("Dobby has finished his performance!")

    def set_face_location(self, x, y):
        self.target_y = y
        self.target_x = x
        if (self.is_seeking):
            self.lockFace()
   
    def set_no_face(self):
        if (self.is_locked):
            self.lostFace()

    def set_gesturing(self, gesture: gestureRequestMessage):
        self.startGesture()
        time.sleep(gesture.duration_seconds + 1)
        self.lostFace()
        
        

