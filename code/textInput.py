import batFramework as bf

import pygame

class TextInput(bf.Button):
    def __init__(self):
        super().__init__("")
        self.cursor_position = 0
        self.controls = bf.ActionContainer(
            bf.Action("backspace").add_key_control(pygame.K_BACKSPACE),
            bf.Action("escape").add_key_control(pygame.K_ESCAPE),
            bf.Action("return").add_key_control(pygame.K_RETURN)
        )
        self.cursor_speed = 20
        self.cursor_counter = 0
        self.set_padding((8,4))
        self.on_changed_callback = None
        self.on_return_callback = None


    def to_string_id(self)->str:
        return "TextInput"

    def set_on_changed_callback(self,callback):
        self.on_changed_callback = callback
        return self

    def set_on_return_callback(self,callback):
        self.on_return_callback = callback
        return self
        
    def do_process_actions(self,event):
        super().do_process_actions(event)
        self.controls.process_event(event)

    def do_reset_actions(self):
        super().do_reset_actions()
        self.controls.reset()

    def update(self,dt):
        if self.is_focused:    self.cursor_counter += 60*dt

    def do_handle_event(self,event)->None:
        res = False
        if self.click_action.is_active():
            root = self.get_root()
            if root.hovered ==  self:
                if not self.is_focused :  self.get_focus()
                pygame.key.start_text_input()
                res = True
            else:
                pygame.key.start_text_input()


        if self.is_focused:
            res = True
            if event.type == pygame.TEXTINPUT:
                self.set_text(self._text + event.text)            
            elif self.controls.is_active("backspace"):
                self.set_text(self._text[:-1])
            elif self.controls.is_active("escape"):
                self.lose_focus()
            elif self.controls.is_active("return"):
                if self.on_return_callback: self.on_return_callback()
                self.lose_focus()
            else:
                res = False
        return res


    def set_text(self,text):
        super().set_text(text)
        self.apply_constraints()

    def build(self):
        bf.Label.build(self)


    def draw(self,camera):
        draw_cursor = False
        if self._font_object and self.cursor_counter > self.cursor_speed and self.is_focused:
            if self.cursor_counter > 2* self.cursor_speed :
                self.cursor_counter = 0
            draw_cursor = True
        res = super().draw(camera)
        if not res : return res
        if draw_cursor:
            pygame.draw.rect(
                camera.surface,
                self._text_color,
                camera.transpose(
                    pygame.FRect(*self._text_rect.move(*self.rect.topleft).topright,min(4,self._font_object.point_size//8),self._font_object.point_size).inflate(0,-4)
                )
            )
        return res
