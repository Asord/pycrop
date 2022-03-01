from math import sqrt, atan2

def pad(v, _min, _max):
    return int(max(min(v, _max), _min))

def vecPad(vec, v_min, v_max):
    return Vec2(
        max(min(vec.x, v_max.x), v_min.x),
        max(min(vec.y, v_max.y), v_min.y)
    )


def RectToOriginDim(p1, p2):
    """
    Transform a two point rect to a point-dim one
    """
    _upper_left = Vec2(
        min(p1.x, p2.x),
        min(p1.y, p2.y)
    )

    _lower_right = Vec2(
        max(p1.x, p2.x),
        max(p1.y, p2.y)
    )

    return [_upper_left, _lower_right-_upper_left]

def RectToWHXY(p1, p2):
    _origin_dim = RectToOriginDim(p1, p2)
    return [_origin_dim[1], _origin_dim[0]]

class Vec2:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '{:g}i + {:g}j'.format(self.x, self.y)

    def __repr__(self):
        return repr((self.x, self.y))

    def dot(self, other):
        if not isinstance(other, Vec2):
            raise TypeError('Can only take dot product of two Vector2D objects')
        return self.x * other.x + self.y * other.y

    __matmul__ = dot

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vec2(self.x*scalar, self.y*scalar)
        raise NotImplementedError('Can only multiply Vector2D by a scalar')

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar):
        return Vec2(self.x % scalar, self.y % scalar)

    def __abs__(self):
        return sqrt(self.x**2 + self.y**2)

    def distance_to(self, other):
        return abs(self - other)

    def to_polar(self):
        return self.__abs__(), atan2(self.y, self.x)

    def tuple(self):
        return self.x, self.y

    def scale(self, vScale):
        if isinstance(vScale, Vec2):
            return Vec2(int(self.x*vScale.x), int(self.y*vScale.y))
        raise NotImplementedError("Can only scale from a vector")

    def getScale(self, vOther):
        if isinstance(vOther, Vec2):
            return Vec2(self.x/vOther.x, self.y/vOther.y)
        raise NotImplementedError("Can only get scale from two vectors")