import batFramework as bf
import pygame
import code

bf.init((240,160),pygame.SCALED,default_text_size=16)


bf.Manager(code.TitleScene()).run()

