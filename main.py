import batFramework as bf
import pygame
import scenes

bf.init((480,300),pygame.SCALED,default_text_size=8,resource_path='data',default_font="fonts/p2p.ttf",fps_limit=60)
# bf.init((640,480),pygame.SCALED,default_text_size=48)


bf.Manager(
    scenes.TitleScene(),
    scenes.MainScene()
).run()

