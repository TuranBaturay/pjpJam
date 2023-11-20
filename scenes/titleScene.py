import batFramework as bf
from .custom_scene import CustomScene
from .dialogueBox import DialogueBox
import pygame

class TitleScene(CustomScene):
    def __init__(self):
        super().__init__("title")
        self.set_clear_color("gray30")

    def do_when_added(self):
        self.root.add_child(bf.Image("assets/sprites/bg.png"))
        title = bf.Label("Make it").set_text_size(28)
        self.root.add_child(title)
        title.set_center(*self.hud_camera.rect.move(0,40).midtop)
        title2 = bf.Label("BLOOM").set_text_size(36)
        self.root.add_child(title2)
        title2.set_text_color("yellow")
        title2.set_center(*title.rect.move(0,20).midbottom)



        container = bf.Container(bf.Column(gap = 10).set_child_constraints(bf.ConstraintPercentageWidth(0.9,False),bf.ConstraintCenterX()))
        container.set_size(100,60).set_padding(10).set_y(self.hud_camera.get_center()[1]+40)
        container.add_constraints(bf.ConstraintCenterX())
        container.add_child(
            bf.Button("Play",lambda : self.manager.set_scene("main")),
            bf.Button("Quit", self.manager.stop)
        )
        self.root.add_child(container)


        
