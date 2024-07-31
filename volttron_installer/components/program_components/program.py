#program.py
from flet import *

# holds global variables for each individual program such as title, page and what not for
# better clarity and modularbility
class Program:
    def __init__(self, title: str, page: Page, added_agents: list) -> None:
        self.title = title
        self.page = page
        self.added_agents = added_agents
        self.activity = "OFF" # OFF by default