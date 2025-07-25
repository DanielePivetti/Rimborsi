from markupsafe import Markup

def nl2br(value):
    """Convert newlines to <br> tags."""
    if value:
        return Markup(value.replace('\n', '<br>\n'))
    return value
