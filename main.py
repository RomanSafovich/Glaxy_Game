from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder

Config.set("graphics", "width", "900")
Config.set("graphics", "height", "400")
from kivy import platform
import random
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Line, Color, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file("menu.kv")

class GalaxyApp(App):
    pass


def is_desktop():
    if platform in ("win", "linux", "macos"):
        return True
    return False


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, keyboard_closed
    from tiles import get_tile_coordinate, update_tiles, pre_fill_tiles_coordinates, init_tiles, generate_tiles_cooridantes
    perspective_point_x = NumericProperty()
    perspective_point_y = NumericProperty()
    VERTICAL_TOTAL_NUM_OF_LINES = 8
    HORIZONTAL_TOTAL_NUM_OF_LINES = 15
    HORIZONTAL_SPACING = 0.1
    VERTICAL_SPACING = 0.4
    NUM_OF_TILES = 20
    SPEED_Y = 0.8
    SPEED_X = 3.0
    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04

    score_text = StringProperty("Score: 0")
    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_text = StringProperty("START")

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # sound initialization
        self.begin_sound = None
        self.galaxy_sound = None
        self.gameover_impact_sound = None
        self.gameover_voice = None
        self.music1_sound = None
        self.restart_sound = None
        self.init_audio()

        self.galaxy_sound.play()
        self.current_offset_y = 0
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.tile_y_loop = 0
        self.tiles = []
        self.tiles_coordinates = []
        self.vertical_lines = []
        self.horizontal_lines = []
        self.ship = None

        self.menu_widget = ObjectProperty()
        self.state_game_over = False
        self.state_game_started = False
        self.ship_coordinates = [(0, 0), (0, 0), (0, 0)]
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_cooridantes()
        self.init_tiles()
        self.init_ship()

        if is_desktop():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def reset_game(self):
        self.tiles_coordinates = []
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.tile_y_loop = 0
        self.current_offset_y = 0
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_cooridantes()
        self.score_text = "Score: 0"
        self.state_game_over = False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        x1 = center_x - ship_half_width
        y1 = base_y
        x2 = center_x
        y2 = base_y + ship_height
        x3 = center_x + ship_half_width
        y3 = y1
        self.ship_coordinates = [(x1, y1), (x2, y2), (x3, y3)]
        x1_transformed, y1_transformed = self.transform(x1, y1)
        x2_transformed, y2_transformed = self.transform(x2, y2)
        x3_transformed, y3_transformed = self.transform(x3, y3)
        self.ship.points = [x1_transformed, y1_transformed, x2_transformed,
                            y2_transformed, x3_transformed, y3_transformed]

    def check_ship_inside_tile(self):
        for i in range(len(self.tiles_coordinates)):
            tile_x, tile_y = self.tiles_coordinates[i]
            if tile_y > self.tile_y_loop + 1:
                return False
            if self.check_collision_with_tile(tile_x, tile_y):
                return True
        return False

    def check_collision_with_tile(self, tile_x, tile_y):
        x_min, y_min = self.get_tile_coordinate(tile_x, tile_y)
        x_max, y_max = self.get_tile_coordinate(tile_x + 1, tile_y + 1)
        for i in range(len(self.ship_coordinates)):
            ship_point_x, ship_point_y = self.ship_coordinates[i]
            if x_min <= ship_point_x <= x_max and y_min <= ship_point_y <= y_max:
                return True
        return False

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.HORIZONTAL_TOTAL_NUM_OF_LINES):
                self.horizontal_lines.append(Line())


    def get_line_x_from_index(self, index):
        center_line_x = self.perspective_point_x
        offset = index - 0.5
        line_pos_x = int(center_line_x + offset * self.VERTICAL_SPACING * self.width) + self.current_offset_x
        return line_pos_x

    def get_line_y_from_index(self, index):
        line_pos_y = int(index * self.HORIZONTAL_SPACING * self.height - self.current_offset_y)
        return line_pos_y



    def update_horizontal_lines(self):
        '''
        drawing the horizontal lines that are updated from the update func
        which is called every 60 frames per second
        '''
        start_index = -int(self.VERTICAL_TOTAL_NUM_OF_LINES / 2) + 1
        end_index = start_index + self.VERTICAL_TOTAL_NUM_OF_LINES - 1
        x_min = self.vertical_lines[start_index].points[0]
        x_max = self.vertical_lines[end_index].points[0]
        for i in range(self.HORIZONTAL_TOTAL_NUM_OF_LINES):
            line_pos_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_pos_y)
            x2, y2 = self.transform(x_max, line_pos_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]


    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.VERTICAL_TOTAL_NUM_OF_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        '''
           drawing the vertical lines that are updated from the update func
           which is called every 60 frames per second
        '''
        start_index = -int(self.VERTICAL_TOTAL_NUM_OF_LINES / 2) + 1
        for i in range(start_index, start_index + self.VERTICAL_TOTAL_NUM_OF_LINES):
            line_pos_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_pos_x, 0)
            x2, y2 = self.transform(line_pos_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        time_factor = dt * 60
        spacing_y = self.HORIZONTAL_SPACING * self.height
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if not self.state_game_over and self.state_game_started:
            speed_y = self.SPEED_Y * self.height / 100
            self.current_offset_y += speed_y * time_factor
            while self.current_offset_y >= spacing_y:
                self.tile_y_loop += 1
                self.score_text = f"Score: {self.tile_y_loop}"
                self.generate_tiles_cooridantes()
                self.current_offset_y -= spacing_y
            # self.current_offset_x += self.SPEED_X * time_factor
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor
        if not self.check_ship_inside_tile() and not self.state_game_over:
            self.state_game_over = True
            self.music1_sound.stop()
            self.gameover_impact_sound.play()
            self.menu_widget.opacity = 1
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_text = "RESTART"
            Clock.schedule_once(self.play_game_over_voice_sound, 1)

    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.gameover_voice.play()

    def init_audio(self):
        self.begin_sound = SoundLoader.load("./RESOURCES/audio/begin.wav")
        self.galaxy_sound = SoundLoader.load("./RESOURCES/audio/galaxy.wav")
        self.gameover_impact_sound = SoundLoader.load("./RESOURCES/audio/gameover_impact.wav")
        self.gameover_voice = SoundLoader.load("./RESOURCES/audio/gameover_voice.wav")
        self.music1_sound = SoundLoader.load("./RESOURCES/audio/music1.wav")
        self.restart_sound = SoundLoader.load("./RESOURCES/audio/restart.wav")

        self.music1_sound.volume = 1
        self.begin_sound.volume = 0.25
        self.galaxy_sound.volume = 0.25
        self.gameover_impact_sound.volume = 0.6
        self.gameover_voice.volume = 0.25
        self.restart_sound.volume = 0.25


    def on_menu_button_pressed(self):
        if self.menu_button_text == "RESTART":
            self.restart_sound.play()
        else:
            self.begin_sound.play()
        self.music1_sound.play()
        self.reset_game()
        self.state_game_started = True
        self.menu_widget.opacity = 0


GalaxyApp().run()
