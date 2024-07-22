"""
These objects should have the following properties:
    1. Recieve real time status updates such as health, on/off status, num of agents, any stopped agents
    2. Should route to their own unique page where additional modifications can be made

""" 
from flet import *

class ProgramTile(UserControl): # full of monolithic code to see layout
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.activity = "OFF"
        self.colors = {
            "bgcolor": "#9d9d9d" if self.activity =="ON" else colors.with_opacity(0.65, "#9d9d9d"),
            "text_color": "white" if self.activity == "ON" else colors.with_opacity(0.65, "white"),
            "on_off": "#00ff00" if self.activity == "ON" else colors.with_opacity(0.65, "#ff0000")
        }
        
    def build_card(self) -> Container:
        return Container(
            width=150,
            height=150,
            border_radius=25,
            padding=padding.all(10),
            bgcolor=self.colors["bgcolor"],
            on_click=lambda e: print("clicked"), # will lead to individualized page for managing program 
            content=Column(
                controls=[
                    Row(controls=[Text("P1 -", color=self.colors['text_color']), Text(value=f"{self.activity}", color=self.colors['on_off'])]),
                    Row(controls=[Text("Agents"), Text("0")]),
                    Row(controls=[Text("Health"), Text("0")]),
                ]
            )
        )
    
broooo_column = Row(
    wrap=True
)