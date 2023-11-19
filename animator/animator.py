import batFramework as bf
import pygame
import customtkinter
import tkinter.filedialog,tkinter.simpledialog
import os

# print([f for f in pygame.font.get_fonts() if not 'noto' in f])
bf.init(
    (1280,720),
    flags = pygame.SCALED,
    default_text_size = 24,
    vsync = 1,
    default_font = "notosans"
)
bf.utils.load_font("awesome.otf","awesome")

def stylize(*widgets:bf.Widget):
    for widget in widgets:
        if widget.children : stylize(*widget.children)
        w_type = type(widget)
        # print("Stylizing : ",widget.to_string())
        if issubclass(w_type,bf.Shape):
            print(w_type)
            widget.set_color(bf.color.DARK_BLUE).set_border_radius(10).set_outline_color(bf.color.LIGHT_BLUE)
        if issubclass(w_type,bf.Frame):
            widget.set_border_radius(20)
        if issubclass(w_type, bf.Label):
            widget.set_text_color(bf.color.LIGHT_BLUE)



class CustomRoot(bf.Root):
    def __init__(self):
        super().__init__()

    def add_child(self,*children):
        stylize(*children)
        # print(children)
        super().add_child(*children)



class CustomScene(bf.Scene):
    def __init__(self,name):
        super().__init__(name)
        self.remove_hud_entity(self.root)

        self.root  : bf.Root = CustomRoot()
        self.root.set_center(*self.hud_camera.get_center())
        self.add_hud_entity(self.root)
        # self.custom_debugger = CustomDebugger()
        # self.root.add_child(self.custom_debugger)





class NumSelect(bf.Button):
    def __init__(self,value,min_range:int|float=0,max_range:int|float=100,step:float|int=1,num_callback=None,callback=None):
        self.value = value
        self.min_range = min_range
        self.max_range = max_range
        self.num_callback = num_callback
        self.step = step
        super().__init__(str(value),callback)

    def reset(self,val :int = 0):
        self.set_value(val)

    def set_value(self,value:int):  
        self.value = max(min(self.max_range,value),self.min_range)
        self.set_text(str(self.value))
        if self.num_callback : self.num_callback(self.value)    
        
    def do_handle_event(self,event):
        res  = super().do_handle_event(event)
        if res : return res
        if self.is_hovered and event.type == pygame.MOUSEWHEEL:
            self.set_value(self.value + (event.y*self.step))
            return True
        return False

    

def prompt_file():
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(
        parent=top,
        title="Choose a png animation file",
        filetypes = [("PNG Files","*.png")]
    )
    top.destroy()
    return file_name

def prompt_number(prompt_value:str):
    top = tkinter.Tk()
    top.withdraw()  # hide window
    number = tkinter.simpledialog.askinteger(
        parent = top,
        title = "TITLE",
        prompt=prompt_value
    )
    top.destroy()
    return number
    
class MainScene(CustomScene):
    def __init__(self)->None: 
        super().__init__("main")
        self.set_clear_color("gray40")
        self.camera.set_max_zoom(8)
        self.camera.set_min_zoom(0.5)



        self.add_action(
            bf.Action("control").add_key_control(pygame.K_LCTRL,pygame.K_RCTRL).set_holding(),
            bf.Action("open").add_key_control(pygame.K_o),
            bf.Action("zoom_in").add_key_control(pygame.K_UP).set_holding(),
            bf.Action("zoom_out").add_key_control(pygame.K_DOWN).set_holding(),
            bf.Action("space").add_key_control(pygame.K_SPACE),
            bf.Action("save").add_key_control(pygame.K_s),
            bf.Action("left").add_key_control(pygame.K_LEFT),
            bf.Action("right").add_key_control(pygame.K_RIGHT),
            bf.Action("print").add_key_control(pygame.K_p),
            
        )

        # Sprite stuff
        self.sprite = bf.AnimatedSprite().set_center(*self.camera.get_center())
        self.frame_length_list : list[int] = []
        self.animation_speed : float = 1
        self.paused :bool = False

        bottom_frame = bf.Frame(10,10).set_padding(10).add_constraints(bf.ConstraintAnchorBottom(),bf.ConstraintCenterX())

        # Gui
        bottom_layout =bf.Column(gap=4,shrink=True).set_child_constraints(bf.ConstraintCenterX())
        
        #Main container
        self.bottom_container = bf.Container(bottom_layout)
        
        self.indicators = bf.Container(bf.Row(gap = 10,shrink= True))

        self.pause_button = bf.Button("⏸",self.toggle_pause)

        self.save_button = bf.Button("💾",self.save_data)
        
        self.controls = bf.Container(bf.Row(gap=4,shrink=True))
        self.controls.add_child(
            self.save_button.set_font("awesome"),
            bf.Button("⏹",lambda : self.sprite.set_counter(0)).set_font("awesome"),
            bf.Button("⏮",self.previous_frame).set_font("awesome"),
            self.pause_button.set_font("awesome"),
            bf.Button("⏭",self.next_frame).set_font("awesome"),
        )


        self.bottom_container.add_child(self.indicators,self.controls)
        bottom_frame.add_child(self.bottom_container)
        self.root.add_child(
            bottom_frame,
            NumSelect(
                self.animation_speed,
                min_range=0.25,
                max_range= 4,
                step=0.25,
                num_callback = lambda value: self.set_speed(value)
            ).add_constraints(bf.ConstraintAnchorTopRight())
        )
        self.save_file = bf.utils.load_json_from_file("animation_files.json")

        self.current_path = ""
        self.file_list = bf.Container(bf.Column(gap=4,shrink=True)).set_padding(20).add_constraints(bf.ConstraintCenterY())
        self.root.add_child(self.file_list)

        self.load_all_saved_files()

        print(self.root.print_tree())
        stylize(self.root)

    def do_when_added(self):
        self.debugger = bf.Debugger()
        self.debugger.add_dynamic_data("",lambda : str(self.sprite.get_frame_index()) if self.sprite.animStates  else "" )
        self.root.add_child(self.debugger)


    def load_all_saved_files(self):
        i = 0
        self.file_list.clear_children()
        for path,data in self.save_file["files"].items():
            combined_result = f"{os.path.basename(os.path.dirname(path))}/{os.path.basename(path)}"
            b =bf.Button(
                    combined_result,
                    callback = lambda path=path, data = data : self.load_data(path,data["width"],data["height"],data["ffl"])
                )
            b.set_text_size(12)
            stylize(b)
            self.file_list.add_child(b)
            i += 1
            if i >= 10: break

    def set_speed(self,value:float):
        self.animation_speed = value

    def next_frame(self):
        if not self.paused : return
        index = self.sprite.get_frame_index()
        val = self.sprite.float_counter + self.frame_length_list[index]
        self.sprite.set_counter(val)

    def go_to_frame(self,i:int):
        if not self.paused : return
        cumul = sum(self.frame_length_list[:i]) + 1 if i > 0 else 0
        print(i,cumul)
        self.sprite.set_counter(cumul)

    def previous_frame(self):
        if not self.paused : return
        index = self.sprite.get_frame_index()
        val = self.sprite.float_counter - self.frame_length_list[index]
        self.sprite.set_counter(val)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.set_text("▶" if self.paused else "⏸")
    

    def modify(self,index:int,new_value:int):
        delta = new_value - self.frame_length_list[index]
        self.frame_length_list[index] = new_value
        self.sprite.get_state().set_frame_length_list(self.frame_length_list)
        self.sprite.float_counter += delta

    def do_update(self,dt):
        if not self.paused : self.sprite.update(dt*self.animation_speed)


        if self.actions.is_active("zoom_in"): self.camera.zoom_by(0.1)
        if self.actions.is_active("zoom_out"): self.camera.zoom_by(-0.1)
        if self.sprite.animStates :
            index = self.sprite.get_frame_index()
            for i,child in enumerate(self.indicators.children):
                if i == index : 
                    child.set_color(bf.color.DARK_BLUE).set_outline_width(3)
                else:
                    child.set_color(bf.color.CLOUD_WHITE).set_outline_width(0)

    def do_early_draw(self,surface):
        self.sprite.draw(self.camera)

    def save_data(self):
        if not self.sprite.animStates: return
        print(f"SAVE : {self.current_path} with {self.frame_length_list}")
        self.save_file["files"][self.current_path] = {
                "width": int(self.sprite.rect.w),
                "height": int(self.sprite.rect.h),
                "ffl" : self.frame_length_list
            }
        
        bf.utils.save_json_to_file("animation_files.json",self.save_file)
        self.load_all_saved_files()

    def load_data(self,path,width,height,ffl):
        # print(file_path,os.path.basename(file_path).split('.')[0])
        print(f"load {path} with {ffl}")
        self.sprite.remove_animState("default")
        self.sprite.add_animState(
            name="default",
            file = path,
            size = (width,height),
            frame_length_list = ffl
        )
        self.current_path = path
        self.indicators.clear_children()
        self.frame_length_list = self.sprite.get_state().frame_length_list

        for index,i in enumerate(self.sprite.get_state().frame_length_list):
            n  = NumSelect(
                    value=i,
                    min_range = 1,
                    num_callback = lambda value, index=index : self.modify(index,value),
                    callback = lambda index = index: self.go_to_frame(index) 
                )
            stylize(n)
            self.indicators.add_child(n)

    def open_file(self):
        file_path = prompt_file()
        if file_path == (): return
        
        width = prompt_number("width")
        height = prompt_number("height")
        if not width or not height : return
        self.load_data(file_path,width,height,10)
    def do_handle_event(self,event):
        if self.actions.is_active("control","open"): self.open_file()
        if self.actions.is_active("control","save"): self.save_data()
        if self.actions.is_active("space"): self.toggle_pause()

        if self.actions.is_active("left"): self.previous_frame()        
        if self.actions.is_active("right"):
            self.next_frame()
        if self.actions.is_active("print"): print(self.root.to_string())

bf.Manager(MainScene()).run()
