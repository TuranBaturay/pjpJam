import batFramework as bf
from pygame.math import Vector2


class AnimatedParticle(bf.AnimatedSprite,bf.Particle):
    def __init__(self,start_pos,start_vel):
        bf.Particle.__init__(self)
        super().__init__()
        self.set_center(*start_pos)
        self.velocity = Vector2(*start_vel)
    def set_animation(self,path,frame_size,fll:list)->"AnimatedParticle":
        self.add_animState("main",path,frame_size,fll)
        self.set_animState("main")
        print("NEW",self.animStates)
        return self

    def update(self, dt: float):
        if not self.animStates or self.dead : return
        self.float_counter += 60 * dt
        if self.float_counter > self.get_state().ffl_length:
            self.kill()
        self.do_update(dt)
        delta = self.velocity * dt
        self.rect.move_ip(*delta)


    def update_surface(self):
        self.surface = self.get_state().get_frame(self.float_counter, self.flipX)
