from Rational import Rational
import math

type Number = Complex | int | Rational | int

class Complex:
    a: int | Rational
    b: int | Rational

    def __new__(cls, *args):
        if len(args) == 0: return 0
        if len(args) == 1:
            if isinstance(args[0], tuple) or isinstance(args[0], list):
                point = tuple(args[0])
        else: point = args
        if len(point) > 2 or type(point[0]) not in (Rational, int, float) or type(point[1]) not in (Rational, int, float): raise TypeError
        if point[1] == 0: return Rational(point[0])
        cls.point = (Rational(point[0]), Rational(point[1]))
        instance = super().__new__(cls)
        return instance

    def __init__(self, *args):
        args = self.point
        if len(args) == 1:
            if isinstance(args[0], tuple) or isinstance(args[0], list):
                self.a = args[0][0]
                self.b = args[0][1]
                return
        self.a = args[0]
        self.b = args[1]
        if len(args) > 2 or type(self.a) not in (Rational, int, float) or type(self.b) not in (Rational, int, float):
            raise TypeError

    def __add__(self, other: Number):
        if type(other) is Complex:
            return Complex(self.a + other.a, self.b + other.b)
        if type(other) is int or type(other) is Rational or type(other) is float:
            return Complex(self.a + Rational(other), self.b)
        raise TypeError

    def __radd__(self, other: Number):
        return self + other

    def __sub__(self, other: Number):
        if type(other) is Complex:
            return Complex(self.a - other.a, self.b - other.b)
        if type(other) is int or type(other) is Rational or type(other) is float:
            return Complex(self.a - Rational(other), self.b)

    def __rsub__(self, other: Number):
        return -self + other

    def __mul__(self, other: Number):
        if type(other) in (int, Rational, float):
            return Complex(Rational(other) * self.a, Rational(other) * self.b)
        return Complex(self.a * other.a - self.b * other.b, self.a * other.b + self.b * other.a)

    def __rmul__(self, other: Number):
        return self * other

    def __truediv__(self, other: Number):
        if type(other) in (Rational, int, float):
            return Complex(self.a / Rational(other), self.b / Rational(other))
        return (self * other.conj()) / (other * other.conj())

    def __rtruediv__(self, other: Number):
        return (other * self.conj()) / (self * self.conj())

    def __floordiv__(self, other : Number):
        if type(other) in (Rational, int, float):
            return Complex(self.a // Rational(other), self.b / Rational(other))
        return (self * other.conj()) // (other * other.conj())

    def __rfloordiv__(self, other: Number):
        return (other * self.conj()) // (self * self.conj())

    def __eq__(self, other: Number):
        return type(other) is Complex and other.a == self.a and other.b == self.b

    def __hash__(self):
        return hash((self.a, self.b))

    def __invert__(self):
        return self.conj()

    def conj(self):
        return Complex(self.a, -self.b)

    def __abs__(self):
        return math.sqrt(self.a ** 2 + self.b ** 2)

    @property
    def real(self):
        return self.a

    @property
    def imag(self):
        return self.b

    @real.setter
    def real(self, value: int | Rational | float):
        self.a = value

    @imag.setter
    def imag(self, value: int | Rational | float):
        self.b = value

    @property
    def norm(self):
        return abs(self)

    @property
    def theta(self):
        return math.atan2(self.a, self.b)

    @norm.setter
    def norm(self, value: int | Rational | float):
        point: Complex = ((self / self.norm) * value)
        self.a = point.a
        self.b = point.b

    @theta.setter
    def theta(self, value: int):
        norm = self.norm
        self.a, self.b = norm * math.cos(value), norm * math.sin(value)

    def __repr__(self):
        if self.real == 0:
            if self.imag == 1:
                return 'i'
            if self.imag == -1:
                return '-i'
            return f'{self.imag}i'
        if self.imag > 0:
            return f'{self.real} + {self.imag}i'
        return f'{self.real} - {-self.imag}i'

    def __neg__(self):
        return Complex(-self.a, -self.b)

    def __pos__(self):
        return Complex(self.a, self.b)

    def __str__(self):
        if self.real == 0:
            if self.imag == 1:
                return 'i'
            if self.imag == -1:
                return '-i'
            return f'{self.imag}i'
        if self.imag > 0:
            return f'{self.real} + {self.imag}i'
        return f'{self.real} - {-self.imag}i'

    def __contains__(self, item): # for zfc
        return item == self.a or item == self.b