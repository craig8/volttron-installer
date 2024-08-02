# program.py

from flet import Page

class SiblingCommunicator:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, subscriber):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)

    def publish(self, event_type, data=None):
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                subscriber(data)

class Program:
    def __init__(self, title: str, page: Page, generated_url: str, event_bus: SiblingCommunicator) -> None:
        self.title = title
        self.page = page
        self.generated_url = generated_url
        self.added_agents = []
        self.activity: str = "OFF"  # OFF by default
        self.event_bus: SiblingCommunicator = event_bus  # Initialize the sibling communicator

    def flip_activity(self) -> None:
        self.activity = "OFF" if self.activity == "ON" else "ON"
        print(f"Program: I turned activity to: {self.activity}")

    def send_signal(self, data):
        print("Program: Sending signal with data")  # Debug print
        self.event_bus.publish("process_data", data)


def create_sibling_communicator():
    return SiblingCommunicator()
