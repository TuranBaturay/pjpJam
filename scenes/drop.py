from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .level import Level

import batFramework as bf
import pygame
from .game_constants import GameConstants as gconst


def world_to_grid(x,y):
    return int(x//gconst.TILE_SIZE),int(y//gconst.TILE_SIZE)


class Drop(bf.DynamicEntity):
    def __init__(self,position: tuple,poison:bool = False) -> None:
        super().__init__((16,16), convert_alpha=True)
        self.set_center(*position)
        image = "poison" if poison else "drop"
        self.surface = pygame.image.load(bf.utils.get_path(f"assets/sprites/{image}.png")).convert_alpha()
        self.collision_rect = pygame.FRect(0,0,8,14) 
        self.add_tag(image)
        self.level_link = None
    def get_bounding_box(self):
        yield self.collision_rect
    def on_collideY(self, collider: bf.DynamicEntity):
        return collider.rect.colliderect(self.collision_rect)
    
    def on_collideX(self, collider: bf.DynamicEntity):
        return collider.rect.colliderect(self.collision_rect)
    

    def do_when_added(self):
        self.level_link : Level= self.parent_scene.get_sharedVar("level")

    def kill(self):
        self.parent_scene.remove_world_entity(self)


    def update(self, dt: float):
        near_tiles = self.level_link.get_neighboring_tiles(*world_to_grid(*self.rect.center),"collider")
        if near_tiles:
            if self.collision_rect.collidelist(near_tiles):
                self.kill()
                return
        self.rect.move_ip(0,2*60*dt)
        self.collision_rect.center = self.rect.center

