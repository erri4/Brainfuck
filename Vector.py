from Rational import Rational
import math

type RawVector = tuple

class Vector:
    point: RawVector

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], tuple) or isinstance(args[0], list):
                self.point = tuple(args[0])
                return
        self.point = args

    @classmethod
    def nullVector(cls, dim: int):
        return cls((0,) * dim)
    
    @classmethod
    def twoPoints(cls, start: RawVector, end: RawVector):
        return cls(start) - cls(end)
    
    def __add__(self, other: "Vector | RawVector"):
        if isinstance(other, Vector):
            if self.dim == other.dim:
                coords = tuple(self[i] + other[i] for i in range(self.dim))
                return Vector(coords)
            else: raise DimensionError("Cannot add vectors: vectors has to be the same dimensions")
        if isinstance(other, tuple):
            return self + Vector(other)
        raise TypeError
                
    def __radd__(self, other: RawVector):
        if isinstance(other, tuple):
            return self + Vector(other)
        raise TypeError

    def __sub__(self, other: "Vector | RawVector"):
        if isinstance(other, Vector):
            if self.dim == other.dim:
                coords = tuple(self[i] - other[i] for i in range(self.dim))
                return Vector(coords)
            else: raise DimensionError("Cannot add vectors: vectors has to be the same dimensions")
        return self + (-Vector(other))
    
    def __rsub__(self, other: RawVector):
        return -self + other

    def __mul__(self, other: "Vector | RawVector | Rational"):
        if isinstance(other, int):
            return Vector(tuple(x * other for x in self.point))
        if isinstance(other, Rational):
            return Vector(tuple(x * other for x in self.point))
        if isinstance(other, float):
            if round(other) == other: other = round(other)
            return Vector(tuple([round(x * other, 7) for x in self.point]))
        if isinstance(other, Vector):
            if self.dim == other.dim:
                dot = 0
                for i in range(self.dim):
                    dot += self[i] * other[i]
                return dot
            raise DimensionError("Cannot dot product vectors: vectors has to be the same dimensions")
        if isinstance(other, tuple):
            if len(other) == self.dim:
                dot = 0
                for i in range(self.dim):
                    dot += self[i] * other[i]
                return dot
            raise DimensionError("Cannot dot product vectors: vectors has to be the same dimensions")
        if type(other).__name__ == 'Matrix':
            return type(other)([list(self.point)]).T() * other
        raise TypeError

    def __rmul__(self, other: "RawVector | int"):
        return self * other

    def __matmul__(self, other: "Vector | RawVector"):
        if isinstance(other, Vector):
            if self.dim == other.dim:
                if self.dim == 2: return self.x * other.y - self.y * other.x
                if self.dim == 3: return Vector((Vector(self.y, self.z)@Vector(other.y, other.z), -(Vector(self.x, self.z)@Vector(other.x, other.z)), Vector(self.x, self.y)@Vector(other.x, other.y)))
                raise DimensionError('Cross product only defined on 3D')
            raise DimensionError("Cannot cross product vectors: vectors has to be the same dimensions")
        if isinstance(other, tuple):
            if len(other) == self.dim:
                if self.dim == 2: return self.x * other[1] - self.y * other[0]
                if self.dim == 3: return Vector((Vector(self.y, self.z)@Vector(other[1], other[2]), -(Vector(self.x, self.z)@Vector(other[0], other[2])), Vector(self.x, self.y)@Vector(other[0], other[1])))
                raise DimensionError('Cross product only defined on 3D')
            raise DimensionError("Cannot cross product vectors: vectors has to be the same dimensions")
    
    def __rmatmul__(self, other: "RawVector"):
        return Vector(other) @ self

    def angle(self, other: "Vector | RawVector"):
        if isinstance(other, Vector):
            if self.dim == other.dim:
                return math.acos(abs(self * other) / (abs(self) * abs(other)))
            raise DimensionError("Cannot find angle between vectors: vectors has to be the same dimensions")
        if isinstance(other, tuple):
            if len(other) == self.dim:
                return self.angle(Vector(other))
            raise DimensionError("Cannot find angle between vectors: vectors has to be the same dimensions")
            
    def projection(self, other: "Vector | RawVector"):
        if isinstance(other, Vector):
            if self.dim == other.dim:
                return ((self * Vector(other)) / (abs(Vector(other)) ** 2)) * Vector(other)
            raise DimensionError("Cannot find angle between vectors: vectors has to be the same dimensions")
        if isinstance(other, tuple):
            if len(other) == self.dim:
                return self.projection(Vector(other))
            raise DimensionError("Cannot find angle between vectors: vectors has to be the same dimensions")

    def __floordiv__(self, other: "Vector | RawVector"):
        return self.projection(other)
    
    def __truediv__(self, other: int | Rational | float):
        return self * (1 / other)

    def __getitem__(self, key: int):
        return self.point[key]

    def __setitem__(self, key: int, value):
        tmp = list(self.point)
        tmp[key] = value
        self.point = tuple(tmp)

    def __delitem__(self, key: int):
        del self.point[key]
    
    @property
    def dim(self):
        return len(self.point)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]
    
    @property
    def z(self):
        if self.dim < 3: raise DimensionError("Vector does not have z value")
        return self[2]
    
    @property
    def norm(self):
        return abs(self)
    
    @property
    def theta(self):
        if self.dim > 2: raise DimensionError("3D+ vectors does not have an angle")
        return math.atan2(self.y, self.x)
    
    @x.setter
    def x(self, value: int | Rational | float):
        self.point = (value,) + self.point[1:]

    @y.setter
    def y(self, value: int | Rational | float):
        self.point = self.point[:1] + (value,) + self.point[2:]

    @z.setter
    def z(self, value: int | Rational | float):
        if self.dim < 3: raise DimensionError("Vector does not have z value")
        self.point = self.point[:2] + (value,) + self.point[3:]

    @norm.setter
    def norm(self, value: int | Rational | float):
        self.point = (~self * value).point

    @theta.setter
    def theta(self, value: int):
        if self.dim > 2: raise DimensionError("3D+ vector does not have an angle")
        norm = self.norm
        self.point = (norm * math.cos(value), norm * math.sin(value))

    def __abs__(self):
        return self.dim

    def __or__(self, other: "Vector | RawVector"):
        return self.angle(other)

    def __neg__(self):
        return self * -1
    
    def __pos__(self):
        return Vector(self)
    
    def __invert__(self) -> "Vector":
        return self / abs(self)

    def __str__(self):
        return str(self.point)

    def __repr__(self):
        return repr(self.point)

    def __eq__(self, other: "Vector | tuple"):
        if type(other) is Vector:
            return self.point == other.point
        if type(other) is tuple:
            return self.point == other
        return False

    def __hash__(self):
        return hash(self.point)

    def __contains__(self, item): # for zfc
        return item in self.point

class DimensionError(Exception): pass
