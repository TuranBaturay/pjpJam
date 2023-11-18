import batFramework as bf
from .custom_scene import CustomScene


class MainScene(CustomScene):
    def __init__(self):
        super().__init__("main")


    def do_when_added(self):
        self.root.add_child(
            bf.Button("TITLE",lambda : self.manager.set_scene("title"))
        )
