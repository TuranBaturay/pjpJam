import batFramework as bf
import pygame
from scenes import Level,Tile,TextInput
from scenes import gconst as constants


TILE_SIZE = constants.TILE_SIZE

bf.init((640,360),flags = pygame.SCALED,default_text_size=16,resource_path = "data",fps_limit=60)


WIDTH,HEIGHT = bf.const.RESOLUTION

x,y = int(WIDTH /TILE_SIZE) + 2, int(HEIGHT/TILE_SIZE) + 2
print(x,y)
tileset = bf.Tileset.load_tileset("assets/tilesets/tileset.png","main",TILE_SIZE)




        
class TileSelector(bf.Indicator):
    def __init__(self):
        super().__init__(TILE_SIZE,TILE_SIZE)
    def to_string_id(self):
        return "TileSelector"
    
    def _build_indicator(self):
        self.surface.fill((0,0,0,0))
        pygame.draw.rect(self.surface,bf.color.DARK_RED,self.surface.get_rect(),3)

class Grid(bf.Entity):
    def __init__(self):
        super().__init__((x*32,y*32),convert_alpha = True)
        self.generate_grid()
    def generate_grid(self)->None:
        self.surface.fill((0,0,0,0))
        right,bottom = self.rect.right,self.rect.bottom
        for i in range(y):
            pygame.draw.line(self.surface,"black",(0,i*TILE_SIZE),(right,i*TILE_SIZE))
        for j in range(x):
            pygame.draw.line(self.surface,"black",(j*TILE_SIZE,0),(j*TILE_SIZE,bottom))
            

class MainScene(bf.Scene):
    def __init__(self):
        super().__init__("main")
        self.set_clear_color("gray20")
        self.add_action(
            bf.Action("save").add_key_control(pygame.K_s),
            bf.Action("load").add_key_control(pygame.K_l),
            bf.Action("undo").add_key_control(pygame.K_z),
            bf.Action("redo").add_key_control(pygame.K_r),
            bf.Action("editor").add_key_control(pygame.K_e),
            bf.Action("tilemap").add_key_control(pygame.K_t),
            bf.Action("inspect").add_key_control(pygame.K_i).set_holding(),
            bf.Action("up").add_key_control(pygame.K_UP),
            bf.Action("left").add_key_control(pygame.K_LEFT),
            bf.Action("down").add_key_control(pygame.K_DOWN),
            bf.Action("right").add_key_control(pygame.K_RIGHT),
            bf.Action("pick").add_mouse_control(2),
            bf.Action("click").add_mouse_control(1).set_holding(),
            bf.Action("click_r").add_mouse_control(3).set_holding(),
            bf.Action("move").add_mouse_control(pygame.MOUSEMOTION).set_holding(),
            bf.Action("control").add_key_control(pygame.K_LCTRL,pygame.K_RCTRL).set_holding()
            
        )
        self.tool : str = "brush"
        self.mode : str = "editor" 

    def do_when_added(self):
        self.tilemap_image =bf.Image(tileset.surface).add_tag("tilemap_mode")
        self.grid = Grid().add_tag("editor_mode")
        self.root.add_child(self.tilemap_image)
        self.add_hud_entity(self.grid)

        topright = bf.Container(bf.Column(gap=4,shrink=True)).add_constraints(bf.ConstraintAnchorTopRight())
        # topright.set_padding(10)

        self.tool_label = bf.Label("")
        self.mode_label = bf.Label("")
        topright.add_child(self.mode_label,self.tool_label)
        self.root.add_child(topright)




        self.tile_selector = TileSelector().add_tag("tilemap_mode")
        self.tile_indicator = Tile(0,0,(0,0)).add_tag("editor_mode")
        self.root.add_child(self.tile_selector)


        self.bottom_container = bf.Container(bf.Row(gap=4).set_child_constraints(bf.ConstraintCenterY())).add_constraints(bf.ConstraintAnchorBottom(),bf.ConstraintPercentageWidth(1))
        self.bottom_container.add_child(
            bf.Button("TILEMAP",lambda : self.set_mode("tilemap")),
            bf.Button("LEVEL",lambda : self.set_mode("editor")),
        )

        self.side_bar = bf.Container(bf.Column(gap=10,shrink=True))

        frame :bf.Frame = bf.Frame(100,100).set_border_radius(10)
        frame.add_child(self.side_bar)
        frame.set_color((*bf.color.DARK_BLUE,200))
        frame.set_padding(10)
        frame.add_constraints(bf.ConstraintAnchorRight(),bf.ConstraintCenterY())

        self.root.add_child(self.bottom_container,frame)
        self.add_hud_entity(self.tile_indicator)

        self.set_mode("editor")
        self.set_tool("brush")
        self.current_tags = []


        self.inspector :bf.Label = bf.Label("INSPECTOR").set_border_radius(10)
        self.inspector.set_color(bf.color.CLOUD_WHITE)
        self.root.add_child(self.inspector)

        self.root.render_order = 50



        self.history = []
        self.history_index = 0


        self.level = Level(x-2,y-2).add_tag("editor_mode")
        self.level.set_on_change_callback(self.save_state)
        self.save_state()
        self.add_world_entity(self.level)

        self.show_tags(*self.current_tags)




    def save_state(self):
        self.history = self.history[:self.history_index]
        self.history.append(self.level.save())
        self.history_index +=1
        

    def load_state(self,index):
        if index <0 or index >= len(self.history):return
        print("LOADING STATE : ",index)
        self.history_index = index
        print("history_index : ",self.history_index)
        self.level.load(self.history[index],do_callback=False)


    def undo(self):
        if self.history_index == 0: return
        self.load_state(self.history_index-1)

    def redo(self):
        if self.history_index < len(self.history): return
        self.load_state(self.history_index+1)
    

    def show_tags(self,*tags):
        self.current_tags = list(tags)
        self.side_bar.clear_children()

        for tag in tags:
            self.side_bar.add_child(
                bf.Container(
                    bf.Row(gap=4,shrink=True),
                    bf.Label(tag).set_border_radius(10).set_color(bf.color.LIGHT_BLUE),
                    bf.Button("x",lambda tag=tag: self.show_tags(*[t for t in self.current_tags if t!=tag])).set_padding(4).set_color(bf.color.DARK_RED).set_border_radius(10)
                )
            )
        last = bf.Container(bf.Row(gap=4,shrink=True))
        last_text = TextInput().set_border_radius(10)
        last_button = bf.Button("+").set_padding(4).set_color(bf.color.DARK_GREEN).set_border_radius(10)
        last.add_child(last_text,last_button)
        self.side_bar.add_child(last)
        last_text.set_on_return_callback(last_button.click)
        last_button.set_callback(
            lambda last_text = last_text: [
                                        self.show_tags(*self.current_tags + [last_text.get_text()]) if last_text.get_text() not in self.current_tags else None,
                                        self.side_bar.children[-1].children[0].get_focus()
                                        ]
                                    
        )
    def set_tool(self,tool:str):    
        self.tool = tool
        self.tool_label.set_text(tool)
        

    def set_mode(self,mode:str):
        match mode : 
            case "tilemap":
                for c in self.get_by_tags("tilemap_mode"): c.set_visible(True) 
                for c in self.get_by_tags("editor_mode"): c.set_visible(False) 
                

                
            case "editor":
                for c in self.get_by_tags("tilemap_mode"):c.set_visible(False) 
                for c in self.get_by_tags("editor_mode"): c.set_visible(True) 
                
            case _ : 
                return

        self.mode =  mode
        self.mode_label.set_text(self.mode)


    def get_hud_mouse_and_index(self):
        x,y = self.hud_camera.convert_screen_to_world(*pygame.mouse.get_pos())
        x_index = int(x // TILE_SIZE)
        y_index = int(y // TILE_SIZE)
        x = x_index * TILE_SIZE
        y = y_index * TILE_SIZE
        return x,y,x_index,y_index
    def get_mouse_and_index(self):
        x,y = self.camera.convert_screen_to_world(*pygame.mouse.get_pos())
        x_index = int(x // TILE_SIZE)
        y_index = int(y // TILE_SIZE)
        x = x_index * TILE_SIZE
        y = y_index * TILE_SIZE
        return x,y,x_index,y_index
    def pick(self,update_tags :bool= False):
        x,y,x_index,y_index = self.get_mouse_and_index()
        if self.mode == "editor":
            t : Tile= self.level.get_tile(x_index,y_index)
            if t:
                data = t.save()
                self.tile_indicator.reset(0,0,data["index"],*data["tags"])
                self.tile_indicator.set_center(*pygame.mouse.get_pos())
        if update_tags:  self.show_tags(*self.tile_indicator.tags)

    def on_click_r(self):
        x,y,x_index,y_index = self.get_mouse_and_index()
        if self.mode == "editor":
            if self.tool == "brush" :
                self.level.remove_tile(x_index,y_index)
    def on_click(self):
        x,y,x_index,y_index = self.get_mouse_and_index()
        x2,y2,x2_index,y2_index = self.get_hud_mouse_and_index()

        if self.mode == "tilemap":
            if self.tool == "brush":
                if not tileset.get_tile(x2_index,y2_index): return
                res = self.tile_indicator.set_index((x2_index,y2_index))
                if res : self.tile_selector.set_position(x2,y2)
        elif self.mode == "editor":
            if self.tool == "brush":
                self.level.add_tile(x_index,y_index,self.tile_indicator.index,*self.current_tags)
    def do_handle_actions(self):

        if self.root.focused.to_string_id() == "TextInput": return
        if self.actions.is_active("editor"):
            self.set_mode("editor")        
        if self.actions.is_active("tilemap"):
            self.set_mode("tilemap")
        if self.actions.is_active("click"):
            self.on_click()        
        if self.actions.is_active("click_r"):
            self.on_click_r()
        if self.actions.is_active("pick"):
            self.pick(self.actions.is_active("control"))        

        if self.actions.is_active("move"):
            data = self.actions.get("move").data
            self.tile_indicator.set_center(*data["pos"])
        if self.actions.is_active("control","save"):
            data = self.level.save()
            print("Result: ",  bf.utils.save_json_to_file("levels/1.json",data))

        if self.actions.is_active("control","load"):
            data = bf.utils.load_json_from_file("levels/1.json")
            if data :
                self.level.load(data)

        if self.actions.is_active("control","undo"):
            self.undo()
            print("UNDO")
        elif self.actions.is_active("control","redo"):
            self.redo()
            print("REDO")

        if self.actions.is_active("left"):
            self.camera.move(-TILE_SIZE,0)
        if self.actions.is_active("right"):
            self.camera.move(TILE_SIZE,0)
        if self.actions.is_active("up"):
            self.camera.move(0,-TILE_SIZE)
        if self.actions.is_active("down"):
            self.camera.move(0,TILE_SIZE) 
        self.inspector.set_visible(self.actions.is_active("inspect"))
        self.tile_indicator.set_visible(not self.actions.is_active("inspect"))

    def do_update(self,dt):
        if self.inspector.visible:
            self.inspector.set_position(*pygame.mouse.get_pos())
            _,_,x_index,y_index = self.get_mouse_and_index() 
            tile :Tile = self.level.get_tile(x_index,y_index)
            self.inspector.set_text(
                f"{tile.grid_position},{tile.tags}" if tile else "None"
            )
    def do_post_world_draw(self,surface):
        if self.mode != "editor":return
        pygame.draw.rect(
            surface,
            bf.color.DARK_RED,
            self.camera.transpose(self.level.rect),2,
        )
bf.Manager(MainScene()).run()


