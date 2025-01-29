# ====== Imports ======
# Standard library imports
from functools import lru_cache


@lru_cache(maxsize=100)
def center_and_limit(text: str, width: int, trailing_dots: int = 2):
    """
    Centers a given text within a specified width. If the text exceeds the width,
    it truncates the text and appends trailing dots.

    Args:
        text (str): The input text to be processed.
        width (int): The total width within which the text should be centered.
        trailing_dots (int, optional): The number of dots to append when truncating. Defaults to 2.

    Returns:
        str: The formatted text, either centered or truncated with dots.
    """
    return (
        (text[: width - trailing_dots] + "." * trailing_dots)  # Truncate and add dots if text is too long
        if len(text) > width
        else text.center(width)  # Otherwise, center the text
    )
