import batFramework as bf
from .custom_scene import CustomScene
from .dialogueBox import DialogueBox
import pygame

class TitleScene(CustomScene):
    def __init__(self):
        super().__init__("title")
        self.set_clear_color("gray30")

    def do_when_added(self):

        container = bf.Container(bf.Column(gap = 10).set_child_constraints(bf.ConstraintPercentageWidth(0.9,False),bf.ConstraintCenterX()))
        container.set_size(100,60).set_padding(10)
        container.add_constraints(bf.ConstraintCenter())
        container.add_child(
            bf.Button("Play",lambda : self.manager.set_scene("main")),
            bf.Button("Quit", self.manager.stop)
        )
        self.root.add_child(container)


        
