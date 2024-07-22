"""
These objects should have the following properties:
    1. Recieve real time status updates such as health, on/off status, num of agents, any stopped agents
    2. Should route to their own unique page where additional modifications can be made

""" 
from flet import *

class ProgramTile(UserControl):

    def __init__(self, page: Page):
        self.card_container = Row()# export to home page and by each added platform, the row continously gets appends
        self.page = page
        self.activity = True
        self.colors = {
            "bgcolor" : "#9d9d9d" if self.activity == True else colors.with_opacity(0.65, self.colors["bgcolor"]),
            "text_color" : "white" if self.activity == True else colors.with_opacity
        }

        #monolithic code to generate a tile 

    def card_container(self)-> Row:
        tile_row = Row()

    def add_card(self, e):
        self.card_container.controls.append()
        self.update()
    
    def build_card(self)-> Container:
        return Container(
            width=150,
            height=150,
            border_radius=25,
            padding=padding.only(left=20, right=20, top=10, bottom=10),

        )