from flet import BoxShadow, colors, ShadowBlurStyle,Offset

def modal_syles()-> dict:
    return {
        "border_radius" : 10,
        "bgcolor" : "#20f4f4f4",
        "shadow" : BoxShadow(
                    spread_radius=1,
                    blur_radius=30,
                    color=colors.BLUE_GREY_300,
                    offset=Offset(0, 0),
                    blur_style=ShadowBlurStyle.OUTER,    
                ),
    }