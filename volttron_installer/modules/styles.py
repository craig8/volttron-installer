from flet import *

def modal_styles()-> dict:
    return {
        "border_radius" : 15,
        "bgcolor" : colors.with_opacity(0.93, "#ffffff"),
        "padding" : 10,
        "blur" : Blur(10,10,BlurTileMode.REPEATED),
        "shadow" : BoxShadow(
                    spread_radius=1,
                    blur_radius=30,
                    color=colors.BLUE_GREY_300,
                    offset=Offset(0,0),
                    blur_style=ShadowBlurStyle.OUTER,
                    ),
    }

def progress_styles()-> dict:
    return {
        "default_color" : "#D2D3D3",
        "completed_color" : "blue",
        "finalized_color": "green",
        "check_color" : "white"
    }