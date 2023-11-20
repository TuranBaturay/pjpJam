import batFramework as bf
import pygame
from .custom_scene import CustomScene
from .player import Player
from .level import Level
from .game_constants import GameConstants as gconst
from .drop import Drop
from .vessel import Vessel
from .cloud import Cloud
import random

class ConstraintAnchorTop(bf.Constraint):
    def __init__(self):
        super().__init__(name="anchor_top")
        
    def evaluate(self, parent_widget,child_widget):
        return  child_widget.rect.top == parent_widget.get_content_top()
        
    def apply_constraint(self,parent_widget,child_widget):
        if not self.evaluate(parent_widget,child_widget):
            child_widget.set_position(child_widget.rect.left,parent_widget.get_content_top())




class MainScene(CustomScene):
    def __init__(self):
        super().__init__("main")
        bf.Tileset.load_tileset("assets/tilesets/tileset.png","main",gconst.TILE_SIZE)
        bf.AudioManager().load_music("theme","music/theme.mp3")
        bf.AudioManager().set_music_volume(0.5)
    def do_when_added(self):
        self.level = Level(40,22)
        self.set_clear_color(bf.color.LIGHT_CYAN)
        # self.camera.zoom()
        self.set_sharedVar("level",self.level)
        # self.root.add_child(
        #     bf.Button("TITLE",lambda : self.manager.set_scene("title"))
        # )

        
        self.pm = bf.ParticleManager()
        self.set_sharedVar("pm",self.pm)
        self.add_world_entity(self.pm)
        d = bf.utils.load_json_from_file("levels/1.json")
        self.level.load(d)
        self.add_world_entity(self.level)
        self.player = Player()
        self.add_world_entity(self.player)
        self.set_sharedVar("player",self.player)
        self.player.set_position(330,175)
        self.camera.set_center(*self.player.rect.center)
        self.camera.set_follow_dynamic_point(self.camera_update)
        self.add_world_entity(Vessel())

        for _ in range(10):
            x,y = random.randint(0,bf.const.RESOLUTION[0]),random.randint(0,bf.const.RESOLUTION[1]//2)
            self.add_world_entity(Cloud((x,y)))
    #  def do_update(self,dt):
        # print(self.level.rect)
        self.score = 0
        self.score_label = bf.Label("0").set_text_size(32)
        self.score_label.set_text_color(bf.color.DARK_BLUE).set_color(bf.color.CLOUD_WHITE)
        frame = bf.Frame(10,10)
        frame.set_color(bf.color.CLOUD_WHITE)
        frame.add_child(self.score_label)
        frame.set_padding(10)
        frame.add_constraints(bf.ConstraintCenterX(),bf.ConstraintPercentageHeight(0.2))
        self.root.add_child(frame)
        
        frame.build_all()
        self.custom_debugger.add_dynamic_data("Player",lambda : self.player.get_state())

        self.spawner = bf.Timer("spawner",700,True,self.spawn_drop,reusable=True)

    def on_enter(self):
        super().on_enter()
        self.spawner.start()
        bf.AudioManager().play_music("theme",-1)

    def on_exit(self):
        super().on_exit()
        self.spawner.stop()

    def do_handle_event(self, event: pygame.Event):
        if event.type == gconst.DROP_EVENT:
            self.score += 1
            self.score_label.set_text(str(self.score))

    def spawn_drop(self):
        for _ in range(0,random.randint(1,3)):
            is_poison = False
            if random.randint(0,3) %2 == 0:
                is_poison = True
            new = Drop((random.randrange(145,510),random.randint(-100,0)),is_poison)
            self.add_world_entity(new)        

    def camera_update(self):
        
        x,y, = self.player.rect.move(0,-bf.const.RESOLUTION[1]/4).center
        x = max(x,self.level.rect.left + self.camera.rect.w/2)
        x = min(x,self.level.rect.right - self.camera.rect.w/2)
        return x,y
