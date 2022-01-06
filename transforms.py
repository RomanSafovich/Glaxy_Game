
def transform(self, x, y):
    '''
    helpful function to go from 2D to perspective
    '''
    # return self.transform_2D(x, y)
    return self.transform_perspective(x, y)


def transform_2D(self, x, y):
    return int(x), int(y)


def transform_perspective(self, x, y):
    linear_y = y * self.perspective_point_y / self.height
    if linear_y > self.perspective_point_y:
        linear_y = self.perspective_point_y
    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - linear_y
    factor_y = diff_y / self.perspective_point_y
    factor_y = factor_y ** 2
    transform_x = self.perspective_point_x + diff_x * factor_y
    transform_y = self.perspective_point_y - factor_y * self.perspective_point_y
    return int(transform_x), int(transform_y)