from typing import TypeAlias
from math import floor, ceil, gcd

Number: TypeAlias = "Rational | int | float"


class Rational:
    # class things

    def __new__(cls, p: int, q: int): # p/q
        if q == 0:
            raise ZeroDivisionError("Division by zero")
        if q < 0:
            q = -q
            p = -p
        gdcpq = gcd(abs(p), q)
        p /= gdcpq
        q /= gdcpq
        if q == 1:
            return int(p)
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, p: int, q: int):
        if q == 0:
            raise ZeroDivisionError("division by zero")
        if q < 0:
            q = -q
            p = -p
        gdcpq = gcd(abs(p), q)
        p /= gdcpq
        q /= gdcpq
        self.p = int(p)
        self.q = int(q)

    @classmethod
    def from_float(cls, num: float | int):
        if type(num) is int: return cls(num, 1)
        return cls(int(str(num).replace('.', '')), 10 ** (len(str(num)[str(num).find('.')+1:])))

    def to_float(self):
        return self.p / self.q

    def __repr__(self):
        return f'{self.p}/{self.q}'

    def __str__(self):
        return f'{self.p}/{self.q}'
    
    # math operators
    
    def __add__(self, other: Number):
        if isinstance(other, Rational):
            return Rational(self.p*other.q + other.p*self.q, self.q*other.q)
        if isinstance(other, int):
            return Rational(self.p + self.q*other, self.q)
        return self + Rational.from_float(other)

        
    def __sub__(self, other: Number):
        return self + (-other)
        
    
    def __mul__(self, other: Number):
        if type(other) is Rational:
            return Rational(self.p*other.p, self.q*other.q)
        if type(other) == int:
            return Rational(self.p*other, self.q)
        return self * Rational.from_float(other)
    

    def __pow__(self, other: Number):
        if type(other) is int:
            return Rational(self.p ** other, self.q ** other)
        if type(other) is Rational:
            if round(self.p ** (1/other.q))**other.q == self.p and round(self.q ** (1/other.q))**other.q == self.q:
                return Rational((round(self.p ** (1/other.q))) ** other.p, (round(self.q ** (1/other.q))) ** other.p)
            return Rational.from_float(((self.p ** (1/other.q))**other.p) / ((self.q ** (1/other.q))**other.p))
        return self ** Rational.from_float(other)

    def __truediv__(self, other: Number):
        if other == 0:
            raise ZeroDivisionError("division by zero")
        if type(other) is Rational:
            return Rational(self.p*other.q, self.q*other.p)
        if type(other) == int:
            return Rational(self.p, self.q*other)
        return self / Rational.from_float(other)
    # right hand operators

    def __rtruediv__(self, other: Number):
        if type(other) is Rational:
            return Rational(other.p*self.q, other.q*self.p)
        if type(other) == int:
            return Rational(other * self.q, self.p)
        return Rational.from_float(other) / self

    def __floordiv__(self, other: Number):
        return floor(self / other)

    def __rfloordiv__(self, other: Number):
            return floor(other / self)
    
    def __radd__(self, other: Number):
        if type(other) is Rational:
            return Rational(self.p*other.q + other.p*self.q, self.q*other.q)
        if type(other) is int:
            return Rational(self.p + self.q*other, self.q)
        return self + Rational.from_float(other)

        
    def __rsub__(self, other: Number):
        return (-self) + other
        
    
    def __rmul__(self, other: Number):
        if type(other) is Rational:
            return Rational(self.p*other.p, self.q*other.q)
        if type(other) == int:
            return Rational(self.p*other, self.q)
        return self * Rational.from_float(other)
    

    def __rpow__(self, other: Number):
        if round(other ** (1/self.q))**self.q == other:
            return round(other ** (1/self.q)) ** self.p
        return Rational.from_float((other ** (1/self.q)) ** self.p)

    # comparators

    def __eq__(self, other: Number):
        if type(other) is Rational:
            return self.p * other.q == self.q * other.p
        if type(other) == int:
            return False
        return self == Rational.from_float(other)
    
    def __le__(self, other: Number):
        diff = (self - other)
        if isinstance(diff, int): return diff <= 0
        return diff.p <= 0 or diff.q < 0
    
    def __lt__(self, other: Number):
        diff = (self - other)
        if isinstance(diff, int): return diff < 0
        return diff.p < 0 or diff.q < 0
    
    def __ne__(self, other: Number):
        diff = (self - other)
        if isinstance(diff, int): return diff != 0
        return diff.p != 0
    
    def __gt__(self, other: Number):
        diff = (self - other)
        if isinstance(diff, int): return diff > 0
        return diff.p > 0 and diff.q > 0
    
    def __ge__(self, other: Number):
        diff = (self - other)
        if isinstance(diff, int): return diff >= 0
        return diff.p >= 0 and diff.q > 0

    # unary operators

    def __invert__(self):
        return 1 / self
    
    def __neg__(self):
        return Rational(-self.p, self.q)
    
    def __pos__(self):
        return Rational(self.p, self.q)
    
    def __abs__(self):
        return Rational(abs(self.p), abs(self.q))
    
    def __round__(self, n: int | None = None):
        if n == 0 or n is None:
            if abs(self - floor(self)) > abs(self - ceil(self)):
                return ceil(self)
            return floor(self)
        return round(self.to_float(), n)

    def __floor__(self):
        return self.p // self.q

    def __ceil__(self):
        return self.p // self.q + 1

    def __hash__(self):
        return hash((self.p, self.q))
