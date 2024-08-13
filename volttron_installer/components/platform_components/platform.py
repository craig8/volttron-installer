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
from volttron_installer.modules.global_configs import global_hosts, global_agents

class ObjectCommunicator:
    """
    A class for facilitating communication between objects through events or signals.

    This class implements a simple publish-subscribe pattern, allowing objects to subscribe
    to specific events and receive notifications when those events are published.

    Attributes:
        _subscribers (dict): A dictionary storing subscribers for each event type.
            The keys are event types (strings), and the values are lists of callable
            objects (functions or methods) that will be invoked when the event is published.

    Example Usage:

    ```python
    # Create an instance of ObjectCommunicator
    communicator = ObjectCommunicator()

    # Define a subscriber function
    def process_data(data):
        print(f"Received data: {data}")

    # Subscribe to the 'my_event' event type
    communicator.subscribe('my_event', process_data)

    # Publish the 'my_event' event with some data
    communicator.publish('my_event', "Hello, world!")

    # Output:
    # Received data: Hello, world!
    ```
    """
    def __init__(self):
        """
        Initializes the ObjectCommunicator with an empty subscribers dictionary.
        """
        # { signal : [** list of subscribers' process_data() functions **]}
        self._subscribers = {}

    def subscribe(self, event_type, subscriber):
        """
        Subscribes an object to a specific event type.

        Args:
            event_type (str): The event type to subscribe to.
            subscriber (callable): The callable object (function or method) that
                will be invoked when the event is published.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)

    def publish(self, event_type, data=None):
        """
        Publishes an event to all subscribers of that event type.

        Args:
            event_type (str): The event type to publish.
            data (any, optional): Data to be passed to the subscribers. Defaults to None.
        """
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

        self.added_hosts = {}
        self.added_agents = {} # agent name : [agent object, custom JSON (defaults to False if none)]
        self.activity: str = "OFF"  # OFF by default
        self.event_bus: ObjectCommunicator = event_bus  # Initialize the Object communicator

    def populate_registered_hosts(self) -> dict:
        pass

    def populate_added_agents(self) -> dict:
        pass

    def flip_activity(self) -> None:
        self.activity = "OFF" if self.activity == "ON" else "ON"
        print(f"Platform: I turned activity to: {self.activity}") # Debug print


def create_sibling_communicator() -> ObjectCommunicator:
    """
    Im going to be honest there is absolutely no purpose for this, you can just create a single instance 
    in `home.py` by importing the object and that can facilitate as the central platform event bus lol.

    Args: None
    """
    return ObjectCommunicator()
