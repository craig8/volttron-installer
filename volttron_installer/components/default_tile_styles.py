from flet import Container, IconButton, colors, padding, Row, icons, MainAxisAlignment, Text

def build_default_tile(content: any) -> Container:
    delete_button = IconButton(
        icon=icons.DELETE,
        #on_click will be re-assigned later 
    )
    return Container(
        border_radius=15,
        padding=padding.only(left=7,right=7,top=5,bottom=5),
        bgcolor=colors.with_opacity(0.5, colors.BLUE_GREY_300),
        content=Row(
            wrap=True,
            controls=[
                Text(value=content),
                delete_button
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )
    )

def build_tile_with_agent_tile(content: Container) -> Container:
    return