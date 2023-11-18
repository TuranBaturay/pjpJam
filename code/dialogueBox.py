import batFramework as bf

class DialogueBox(bf.Label):
    def __init__(self):
        super().__init__("")
        self.messages = []

        
        self.started : bool = False
        self.ended : bool = False
        self.fcounter : float = 0.0
        self.current_message_length :int = 0


    def process_message(self,message):
        self.messages.append(message)

    def queue_message(self,message) ->None:
        self.process_message(message)
        

    def next_message(self) ->None:
        if self.started and self.ended:
            self.ended = False
            self.started = False
            self.messages.pop(0)
        if self.messages :
            self.ended = False
            self.started = True
            self.fcounter = 0
            self.current_message_length = len(self.messages[0])
        else:
            self.set_text("")
    

    def update(self,dt):
        if self.started and not self.ended:
            self.fcounter += min(dt*10,self.current_message_length)
            if self.fcounter == self.current_message_length :
                self.ended = True
            int_counter = int(self.fcounter)
            self.set_text(self.messages[0][:int_counter])        

    
