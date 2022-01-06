import random

from kivy.graphics import Quad, Color


def get_tile_coordinate(self, tile_x, tile_y):
    tile_y -= self.tile_y_loop
    x = self.get_line_x_from_index(tile_x)
    y = self.get_line_y_from_index(tile_y)
    return x, y


def update_tiles(self):
    for i in range(self.NUM_OF_TILES):
        x_min, y_min = self.get_tile_coordinate(self.tiles_coordinates[i][0], self.tiles_coordinates[i][1])
        x_max, y_max = self.get_tile_coordinate(self.tiles_coordinates[i][0] + 1, self.tiles_coordinates[i][1] + 1)
        x1, y1 = self.transform(x_min, y_min)
        x2, y2 = self.transform(x_min, y_max)
        x3, y3 = self.transform(x_max, y_max)
        x4, y4 = self.transform(x_max, y_min)
        self.tiles[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]


def pre_fill_tiles_coordinates(self):
    for i in range(10):
        self.tiles_coordinates.append((0, i))

def init_tiles(self):
    with self.canvas:
        Color(1, 1, 1)
        for i in range(self.NUM_OF_TILES):
            self.tiles.append(Quad())

def generate_tiles_cooridantes(self):
    start_index = -int(self.VERTICAL_TOTAL_NUM_OF_LINES / 2) + 1
    end_index = start_index + self.VERTICAL_TOTAL_NUM_OF_LINES - 1
    last_y = 0
    last_x = 0
    for i in range(len(self.tiles_coordinates) - 1, -1, -1):
        if self.tiles_coordinates[i][1] < self.tile_y_loop:
            del self.tiles_coordinates[i]

    if len(self.tiles_coordinates) > 0:
        last_y = self.tiles_coordinates[-1][1] + 1
        last_x = self.tiles_coordinates[-1][0]
    for _ in range(len(self.tiles_coordinates), self.NUM_OF_TILES):
        self.tiles_coordinates.append((last_x, last_y))
        random_path = random.randint(-1, 1)
        if random_path == -1 and last_x > start_index:  # left tile
            last_x -= 1
            self.tiles_coordinates.append((last_x, last_y))
            last_y += 1
            self.tiles_coordinates.append((last_x, last_y))
        elif random_path == 1 and last_x < end_index - 1:  # right tile
            last_x += 1
            self.tiles_coordinates.append((last_x, last_y))
            last_y += 1
            self.tiles_coordinates.append((last_x, last_y))
        last_y += 1