# program.py

from flet import Page

class SiblingCommunicator:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, subscriber):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)

    def publish(self, event_type, data):
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                subscriber(data)

class Program:
    def __init__(self, title: str, page: Page, generated_url: str, added_agents: list = None, activity: str = "OFF") -> None:
        self.title = title
        self.page = page
        self.generated_url = generated_url
        self.added_agents = added_agents if added_agents else []
        self.activity = activity  # OFF by default
        self.event_bus = SiblingCommunicator()  # Initialize the sibling communicator

    def send_signal(self, data):
        self.event_bus.publish("process_data", data)
