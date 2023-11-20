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
from math import cos

class ConstraintAnchorTop(bf.Constraint):
    def __init__(self):
        super().__init__(name="anchor_top")
        
    def evaluate(self, parent_widget,child_widget):
        return  child_widget.rect.top == parent_widget.get_content_top()
        
    def apply_constraint(self,parent_widget,child_widget):
        if not self.evaluate(parent_widget,child_widget):
            child_widget.set_position(child_widget.rect.left,parent_widget.get_content_top())



class Stem(bf.Entity):
    def __init__(self, position) -> None:
        super().__init__((200,200), convert_alpha=True)
        self.set_center(*position)
        self.surface = pygame.image.load(bf.utils.get_path(f"assets/sprites/stem.png")).convert_alpha()

class Flower(bf.Entity):
    def __init__(self, position) -> None:
        super().__init__((80,80), convert_alpha=True)
        self.set_center(*position)
        self.surface = pygame.image.load(bf.utils.get_path(f"assets/sprites/flower0.png")).convert_alpha()
        self.index = 0
    def set_index(self,index):
        if index < 0 : return
        self.index = index
        self.surface = pygame.image.load(bf.utils.get_path(f"assets/sprites/flower{index}.png")).convert_alpha()

class MainScene(CustomScene):
    def __init__(self):
        super().__init__("main")
        bf.Tileset.load_tileset("assets/tilesets/tileset.png","main",gconst.TILE_SIZE)
        bf.AudioManager().load_music("theme","music/theme.mp3")
        bf.AudioManager().set_music_volume(0.5)
    def do_when_added(self):
        self.level = Level(40,22)
        self.level.render_order = 2
        self.set_clear_color(bf.color.LIGHT_CYAN)
        # self.camera.zoom()
        self.set_sharedVar("level",self.level)
        self.pm = bf.ParticleManager()
        self.set_sharedVar("pm",self.pm)

        self.player = Player()
        self.set_sharedVar("player",self.player)

        # self.root.add_child(
        #     bf.Button("TITLE",lambda : self.manager.set_scene("title"))
        # )
        
    def on_enter(self):
        super().on_enter()
        self.root.children = []
        bf.AudioManager().play_music("theme",-1)
        self.bg = bf.Image("assets/sprites/bg.png")
        self.add_world_entity(self.bg)
        

        self.add_world_entity(self.pm)
        d = bf.utils.load_json_from_file("levels/1.json")
        self.level.load(d)
        self.add_world_entity(self.level)
        self.add_world_entity(self.player)
        self.player.set_position(330,175)
        self.camera.set_center(*self.player.rect.center)
        self.camera.set_follow_dynamic_point(self.camera_update)
        self.add_world_entity(Vessel())


        stem = Stem(self.level.rect.move(0,0).center)
        stem.render_order = 0
        self.add_world_entity(stem)

        self.flower = Flower(stem.rect.move(0,60).midtop)
        self.flower.render_order = 1
        self.add_world_entity(self.flower)

        for _ in range(10):
            x,y = random.randint(0,bf.const.RESOLUTION[0]),random.randint(0,bf.const.RESOLUTION[1]//2)
            self.add_world_entity(Cloud((x,y)))
    #  def do_update(self,dt):
        # print(self.level.rect)
        self.score = 0
        self.score_label = bf.Label("0").set_text_size(32).set_y(10).set_align(bf.Align.CENTER)
        self.root.add_child(self.score_label)
        # frame.set_padding(10)
        self.score_label.add_constraints(bf.ConstraintCenterX())

        self.custom_debugger.add_dynamic_data("Player",lambda : self.player.get_state())

        self.spawner = bf.Timer("spawner",700,True,self.spawn_drop,reusable=True)

        self.spawner.start()
    def on_exit(self):
        super().on_exit()
        self.spawner.stop()

    def do_handle_event(self, event: pygame.Event):
        if event.type == gconst.DROP_EVENT:
            self.score += 1
            self.score_label.set_text(str(self.score))
        if event.type == gconst.POISON_EVENT:
            self.score -= 1
            self.score_label.set_text(str(self.score))       

        self.flower.set_index(int((self.score / 10)))
        if self.score >= 30:
            self.end()

    def end(self):
        self._world_entities = [e for e in self._world_entities if not (e.has_tag("drop") or e.has_tag("poison"))]
        self.spawner.stop()
        l = bf.Label("YOU WIN :)").set_text_size(32)
        l.add_constraints(bf.ConstraintCenter())
        self.root.add_child(l)
        bf.Timer(duration=1000,end_callback=self._sub).start()

    def _sub(self):
        self.root.add_child(
            bf.Button("Menu",
                      callback = lambda : self.manager.set_scene("title") 
            ).set_y(self.hud_camera.rect.bottom-60).add_constraints(bf.ConstraintCenterX())
        )

    def spawn_drop(self):
        for _ in range(0,random.randint(1,3)):
            is_poison = False
            if random.randint(0,3) %2 == 0:
                is_poison = True
            new = Drop((random.randrange(145,510),random.randint(-100,0)),is_poison)
            new.render_order = 4
            self.add_world_entity(new)        

    def camera_update(self):
        
        self.bg.set_center(*self.camera.get_center())
        x,y, = self.player.rect.move(0,-bf.const.RESOLUTION[1]/4).center
        x = max(x,self.level.rect.left + self.camera.rect.w/2)
        x = min(x,self.level.rect.right - self.camera.rect.w/2)
        return x,y
    def do_update(self, dt):
        self.score_label.set_y(
            20 + 5 *cos(pygame.time.get_ticks()*0.003)
        )