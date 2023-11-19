import batFramework as bf
import pygame
from .game_constants import GameConstants as constants


TILE_SIZE = constants.TILE_SIZE
WIDTH,HEIGHT = bf.const.RESOLUTION

x,y = int(WIDTH /32) + 2, int(HEIGHT/32) + 2


class Level(bf.Entity):
    def __init__(self,width,height):
        super().__init__(((x-2)*TILE_SIZE, (y-2)*TILE_SIZE ),convert_alpha = True)
        self.tiles = [[None for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
        self.set_debug_color("indigo")
        self.on_change_callback = None
    def out_of_bounds(self,x,y):
        return x < 0 or x>=self.width or y < 0 or y>=self.height

    def set_on_change_callback(self,callback):
        self.on_change_callback = callback

    def add_tile(self,x,y,index,*tags):
        if self.out_of_bounds(x,y) : return
        t   = self.tiles[y][x]
        new = Tile(x,y,index,*tags)
        if t and new.save() == t.save() : return
        self.tiles[y][x]= new
        self.update_surface()
        if self.on_change_callback: self.on_change_callback()

    def get_tile(self,x,y):
        if self.out_of_bounds(x,y):
            return None
        return self.tiles[y][x]

    def remove_tile(self,x,y):
        if self.out_of_bounds(x,y) : return
        if self.tiles[y][x] == None : return
        self.tiles[y][x] = None
        self.update_surface()
        if self.on_change_callback: self.on_change_callback()


    def update_surface(self):
        self.surface.fill((0,0,0,0))
        for y,row in enumerate(self.tiles):
            for x,tile in enumerate(row):
                if not tile : continue
                self.surface.blit(
                    bf.Tileset.get_tileset("main").get_tile(*tile.index),
                    tile.world_position
                )

    def load(self,data,do_callback:bool=False):
        self.tiles = [[None for _ in range(self.width)] for _ in range(self.height)]
        for y,row in enumerate(data["level"]):
            for x,tile in enumerate(row):
                if not tile : continue
                self.tiles[y][x] = Tile(*tile["grid_position"], tile["index"], *tile["tags"])
        self.update_surface()
        if self.on_change_callback and do_callback: self.on_change_callback()


    def save(self)->dict:
        return {"level":[[t.save() if t else None for t in row] for row in self.tiles]}

    def get_neighboring_tiles(self, gridx: int, gridy: int,*tags):
        res = []
        for x in range(gridx - 2, gridx + 2):
            for y in range(gridy - 2, gridy + 2):
                t = self.get_tile(x, y)
                if not t :continue
                res.append(t)

        if tags : return [tile for tile in res if all(tile.has_tag(t) for t in tags)]
        return res
        
class Tile(bf.DynamicEntity):
    def __init__(self,x,y,index:tuple,*tags):
        super().__init__((TILE_SIZE,TILE_SIZE),convert_alpha=True)
        self.reset(x,y,index,*tags)
    def reset(self,x,y,index,*tags):
        self.add_tag(*tags)
        self.index = index
        self.grid_position = x,y
        self.world_position = x*TILE_SIZE, y*TILE_SIZE
        self.set_index(self.index)
        self.set_position(*self.world_position)
    def on_collideY(self,collider):
        return self.has_tag("collider")

    def on_collideX(self,collider):
        return self.has_tag("collider")

    def set_index(self,index):
        self.index = index
        self.surface.fill((0,0,0,0))
        t = bf.Tileset.get_tileset("main").get_tile(*self.index)
        if t : 
            self.surface.blit(t,(0,0))
            return True
        return False
    def save(self)->dict:
        return {"world_position":self.world_position,"grid_position":self.grid_position,"index":self.index,"tags":self.tags}

