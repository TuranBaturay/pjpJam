import batFramework as bf
from .custom_scene import CustomScene
from .player import Player
from .level import Level
from .game_constants import GameConstants as gconst
class MainScene(CustomScene):
    def __init__(self):
        super().__init__("main")
        bf.Tileset.load_tileset("assets/tilesets/tileset.png","main",gconst.TILE_SIZE)
    def do_when_added(self):
        self.level = Level(40,22)
        self.set_clear_color(bf.color.LIGHT_CYAN)
        # self.camera.zoom()
        self.set_sharedVar("level",self.level)
        self.root.add_child(
            bf.Button("TITLE",lambda : self.manager.set_scene("title"))
        )

        
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
    # def do_update(self,dt):
        # print(self.level.rect)

        self.custom_debugger.add_dynamic_data("Player",lambda : self.player.get_state())


    def camera_update(self):
        
        x,y, = self.player.rect.move(0,-bf.const.RESOLUTION[1]/4).center
        x = max(x,self.level.rect.left + self.camera.rect.w/2)
        x = min(x,self.level.rect.right - self.camera.rect.w/2)
        return x,y
