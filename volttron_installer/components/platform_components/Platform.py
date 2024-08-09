"""
Using shared instances (Composition) seemed more intuitve because 
as this project grows, it would be easier to use this central psuedo database rather than 
parent class that would need constant re-initalization. The shared Instance uses 1
consistent initialized object making state sharing easy. Each object sharing this shared
instance can read and write to the self.variables, allowing each object to react to the 
state changes very easily while allowing these disconnected objects to be as modular as
possible. In heriently, with a shared isntance structure, communictation between different
modules may be less intuitive than inheritance but i believe that this is solved by the ObjectCommunicator
class, which allows for objects to subscribe to and recieve specific signals so they can execute their
own self.functions() or just interpret the data that have been sent from other modules!
"""

from flet import Page

class ObjectCommunicator:
    """An object first subscribes to a specific event_type/signal and inputs their
own self.process_data function via the subscribe method. Then an object can come along 
using the publish method to input an event_type/signal to signal all subscribers of that
signal and pass data into each object's self.process_data
    """
    def __init__(self):
        # { signal : [** list of subscribers' process_data() functions **]}
        self._subscribers = {}

    def subscribe(self, event_type, subscriber):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)

    def publish(self, event_type, data=None):
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                subscriber(data)

class Platform:
    def __init__(self, title: str, page: Page, generated_url: str, event_bus: ObjectCommunicator) -> None:
        self.title = title
        self.page = page
        self.generated_url = generated_url

        self.address = ""
        self.bus_type= "Zmq"
        self.ports = ""

        self.added_agents = {} # agent name : [agent object, custom JSON (defaults to False if none)]
        self.activity: str = "OFF"  # OFF by default
        self.event_bus: ObjectCommunicator = event_bus  # Initialize the Object communicator

    def flip_activity(self) -> None:
        self.activity = "OFF" if self.activity == "ON" else "ON"
        print(f"Platform: I turned activity to: {self.activity}") # Debug print


def create_sibling_communicator():
    return ObjectCommunicator()
