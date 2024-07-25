from flet import Container, colors, Alignment, RadialGradient


def gradial_background() -> Container:
    return Container(
        expand=True,
        gradient=RadialGradient(
            colors=[colors.PURPLE, colors.BLACK],
            radius=1.4,
            center=Alignment(0.8, 0.8)
        )
    )