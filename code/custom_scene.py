import batFramework as bf
from .stylize import stylize
import pygame

class CustomRoot(bf.Root):
    def __init__(self):
        super().__init__()

    def add_child(self,*children):
        stylize(*children)
        print(children)
        super().add_child(*children)

class CustomDebugger(bf.Debugger):

    def __init__(self):
        super().__init__()

    def set_parent_scene(self,scene):
        super().set_parent_scene(scene)
        self.add_data("Resolution",bf.const.RESOLUTION)
        self.add_dynamic_data("FPS",lambda:"" if not self.parent_scene.manager else  str(round(self.parent_scene.manager.get_fps())))
        self.add_dynamic_data("Mouse",pygame.mouse.get_pos)
        self.add_dynamic_data("World", lambda : self.parent_scene.camera.convert_screen_to_world(*pygame.mouse.get_pos()))
        self.add_dynamic_data("Entities", lambda :str(len(self.parent_scene._world_entities)))


class CustomScene(bf.Scene):
    def __init__(self,name):
        super().__init__(name)
        self.remove_hud_entity(self.root)

        self.root  : bf.Root = CustomRoot()
        self.root.set_center(*self.hud_camera.get_center())
        self.add_hud_entity(self.root)

        self.root.add_child(CustomDebugger())
