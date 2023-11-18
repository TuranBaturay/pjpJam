import batFramework as bf
from .dialogueBox import DialogueBox


def apply_common(w:bf.Widget):
    w.set_color(bf.color.DARK_BLUE).set_outline_width(3).set_border_radius(4).set_padding((4,6))

def stylize(*widgets : bf.Widget):
    for w in widgets:
        match w:
            case DialogueBox():
                apply_common(w)
                w.set_padding((10,4))
            case bf.Container():
                stylize(*w.children)
            case bf.Label():
                apply_common(w)
                w.set_antialias(False)

            case bf.Shape():
                apply_common(w)
