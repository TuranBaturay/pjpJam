import batFramework as bf


def check_vertical_overflow(lines, font, max_height):
    linespace = font.get_linesize()
    total_height = len(lines) * linespace

    if total_height > max_height:
        lines_to_keep = []
        lines_height = 0
        
        for line in lines:
            lines_height += linespace
            if lines_height < max_height:
                lines_to_keep.append(line)
            else:
                break

        lines_to_discard = lines[len(lines_to_keep):]
        return '\n'.join(lines_to_keep), ' '.join(lines_to_discard)
    
    return '\n'.join(lines), ''

def insert_newlines(text, font, max_width, max_height):
    words = text.split()
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        width, _ = font.size(test_line)

        if width < max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + ' '

    lines.append(current_line.strip())
    return check_vertical_overflow(lines, font, max_height)



class DialogueBox(bf.Label):
    def __init__(self):
        super().__init__("")
        self.messages = []
        self.started : bool = False
        self.ended : bool = False
        self.fcounter : float = 0.0
        self.counter_speed = 10
        self.current_message_length :int = 0
        self.end_callback = None
    
    def set_end_callback(self,callback):
        self.end_callback = callback
    
    def set_speed(self,value:float)->"DialogueBox":
        self.counter_speed = value
        return self
    def process_message(self,message):
        keep,discard = insert_newlines(message,self._font_object,self.get_content_width(),self.get_content_height())
        self.messages.append(keep)
        if discard:
            self.queue_message(discard)


    def queue_message(self,message) ->None:
        self.process_message(message)
        
    def is_over(self)->bool:
        return self.ended

    def skip(self):
        if self.started and not self.ended:
            self.fcounter = self.current_message_length

    def next_message(self,force:bool=False) ->None:
        if self.started and not self.ended and not force : return 
        if self.started and self.ended:
            self.ended = False
            self.started = False
            self.messages.pop(0)
        elif self.messages: self.set_visible(True)
        if self.messages :
            self.ended = False
            self.started = True
            self.fcounter = 0
            self.current_message_length = len(self.messages[0])
        else:
            self.set_text("")
            self.set_visible(False)
            self.end_callback()

        

    def update(self,dt):
        if self.started and not self.ended:
            self.fcounter = min(self.fcounter + dt*self.counter_speed,self.current_message_length)
            if self.fcounter == self.current_message_length :
                self.ended = True
            self.set_text(self.messages[0][:int(self.fcounter)])        

    
