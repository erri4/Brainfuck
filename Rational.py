from math import floor, gcd

type Number = Rational | int | float


class Rational(int):
    def __new__(cls, p: "int | float | Rational", q: int | None = None): # p/q
        if q is None:
            if type(p) is int: return p
            if type(p) is float:
                return Rational.from_float(p) # Use Rational.from_float(num) not Rational(num)
            if type(p) is Rational:
                return p
        if q == 0 or q is None:
            raise ZeroDivisionError("division by zero")
        if q < 0 and p < 0:
            q = -q
            p = -p
        gdcpq = gcd(p, q)
        p /= gdcpq
        q /= gdcpq
        if q == 1:
            return int(p)
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, p: int, q: int | None = None):
        if q is None:
            return
        if q == 0:
            raise ZeroDivisionError("division by zero")
        gdcpq = gcd(p, q)
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

    def __eq__(self, other: Number):
        if type(other) is Rational:
            return self.p * other.q == self.q * other.p
        if type(other) == int:
            return False
        return self == Rational.from_float(other)
    
    def __le__(self, other: Number):
        diff = (self - other)
        if type(diff) is int: return diff <= 0
        return diff.p <= 0 or diff.q < 0
    
    def __lt__(self, other: Number):
        diff = (self - other)
        if type(diff) is int: return diff < 0
        return diff.p < 0 or diff.q < 0
    
    def __ne__(self, other: Number):
        diff = (self - other)
        if type(diff) is int: return diff != 0
        return diff.p != 0
    
    def __gt__(self, other: Number):
        diff = (self - other)
        if type(diff) is int: return diff > 0
        return diff.p > 0 and diff.q > 0
    
    def __ge__(self, other: Number):
        diff = (self - other)
        if type(diff) is int: return diff >= 0
        return diff.p >= 0 and diff.q > 0

    def __invert__(self):
        return 1 / self
    
    def __neg__(self):
        return Rational(-self.p, self.q)
    
    def __pos__(self):
        return Rational(self.p, self.q)
    
    def __abs__(self):
        return Rational(abs(self.p), abs(self.q))
    
    def __round__(self, n: int):
        if n == 0 or n is None: return self.p // self.q
        return round(self.to_float(), n)

    def __floor__(self):
        return self.p // self.q

    def __ceil__(self):
        return self.p // self.q + 1

    def __hash__(self):
        return hash((self.p, self.q))

    def __contains__(self, item): # for zfc
        return item == self.p or item == self.q
