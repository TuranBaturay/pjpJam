import batFramework as bf
import pygame
import random


class Cloud(bf.Entity):
    def __init__(self, position) -> None:
        super().__init__((128,64), convert_alpha=True)
        self.set_center(*position)
        number = random.randint(1,2)
        self.surface = pygame.image.load(bf.utils.get_path(f"assets/sprites/cloud{number}.png")).convert_alpha()
        self.surface = pygame.transform.scale2x(self.surface)
        self.render_order = random.randint(-11,-1)
        coeff = (abs(self.render_order)) / 11
        self.surface.set_alpha(255- int(0.8*coeff * 255))
        self.speed = (5 - 5/self.render_order) * 0.1

    def reset_left(self):
        self.set_position(0-self.rect.w,random.randint(0,bf.const.RESOLUTION[1]//2))
        if random.randint(0,1) == 1:
            self.surface = pygame.transform.flip(self.surface,True,False)
    def update(self, dt: float):
        self.rect.move_ip(self.speed*60*dt,0)

    def draw(self, camera: bf.Camera) -> int:
        res =super().draw(camera)
        if  self.rect.left > camera.rect.right:
            self.reset_left()
        return res