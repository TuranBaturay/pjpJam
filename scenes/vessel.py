from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .level import Level
    from .player import Player

import batFramework as bf
import pygame
from .game_constants import GameConstants as gconst



def world_to_grid(x,y):
    return int(x//gconst.TILE_SIZE),int(y//gconst.TILE_SIZE)


class Vessel(bf.DynamicEntity):
    def __init__(self) -> None:
        super().__init__((32,16), convert_alpha=True)
        self.surface = pygame.image.load(bf.utils.get_path("assets/sprites/vessel.png")).convert_alpha()
        self.collision_rect = pygame.FRect(0,0,30,8) 
        self.set_uid("vessel")
        self.level_link = None
        self.player_link = None
        self.render_order = 10
    def get_bounding_box(self):
        yield self.collision_rect
    def on_collideY(self, collider: bf.DynamicEntity):

        res =  collider.rect.colliderect(self.collision_rect)
        if not res: return res
        if collider.has_tag("drop"):
            pygame.event.post(gconst.DROP_EVENT)
        elif collider.has_tag("poison"):
            pygame.event.post(gconst.POISON_EVENT)
        return res
    def on_collideX(self, collider: bf.DynamicEntity):
        return collider.rect.colliderect(self.collision_rect)
    

    def do_when_added(self):
        self.player_link = self.parent_scene.get_sharedVar("player")
        self.level_link = self.parent_scene.get_sharedVar("level")
    
    def update(self, dt: float):
        self.set_center(*self.player_link.rect.move(0,-16).center)
        self.collision_rect.midbottom = self.rect.midbottom