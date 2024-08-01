# holds global variables for each individual program such as title, page and what not for
# better clarity and modularbility
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

    def __init__(self, title: str, page: Page, generated_url: str, activity: str = "OFF") -> None:
        self.title = title
        self.sibling_communicator = SiblingCommunicator()
        self.page = page
        self.added_agents: list = []
        self.activity = "OFF"  # OFF by default
        self.generated_url = generated_url

    def __init__(self, event_bus):
        self.event_bus = event_bus

    def send_signal(self, data):
        self.event_bus.publish("process_data", data)

