import batFramework as bf
from .custom_scene import CustomScene
from .dialogueBox import DialogueBox

class TitleScene(CustomScene):
    def __init__(self):
        super().__init__("title")
        self.set_clear_color("gray30")


    def do_when_added(self):

        container = bf.Container(bf.Column(gap = 10).set_child_constraints(bf.ConstraintPercentageWidth(0.9,False),bf.ConstraintCenterX()))
        container.set_size(100,60)
        container.add_constraints(bf.ConstraintCenter())
        container.add_child(
            bf.Button("Play",lambda : self.manager.set_scene("main")),
            bf.Button("Quit", self.manager.stop)
        )
        self.root.add_child(container)


        
        d = DialogueBox().set_autoresize(False)
        d.add_constraints(bf.ConstraintAnchorBottom(),bf.ConstraintCenterX(),bf.ConstraintPercentageWidth(1),bf.ConstraintHeight(40))
        
        self.root.add_child(d)
        d.queue_message("HELLO FOLKS ! HOW DO YOU DO ?")
        d.next_message()
