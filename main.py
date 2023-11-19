import batFramework as bf
import pygame
import code

bf.init((480,300),pygame.SCALED,default_text_size=8,resource_path='data',default_font="fonts/p2p.ttf")
# bf.init((640,480),pygame.SCALED,default_text_size=48)


bf.Manager(
    code.TitleScene(),
    code.MainScene()
).run()

