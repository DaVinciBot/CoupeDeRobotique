def center_and_limit(text: str, width: int, trailing_dots: int = 2):
    return (
        (text[: width - trailing_dots] + "." * trailing_dots)
        if len(text) > width
        else text.center(width)
    )
