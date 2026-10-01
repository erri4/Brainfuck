from Vector import Vector
from itertools import product
from typing import Callable, Any

class Cardinal:
    cards: "dict[tuple[int, bool], Cardinal]" = {}
    isfinite: bool = True
    ordinal: int

    def __new__(cls, card: int = 0, isfinite: bool = True):
        if cls.cards.get((card, isfinite), None) is None:
            cls.cards[(card, isfinite)] = super().__new__(cls)
        return cls.cards[(card, isfinite)]

    def __init__(self, card: int = 0, isfinite: bool = True):
        self.ordinal = card
        self.isfinite = isfinite

    def __eq__(self, other: "ZFCSet | Cardinal | int"):
        if type(other) is int:
            return self.isfinite and self.ordinal == other
        if type(other) is Cardinal:
            return self.isfinite == other.isfinite and self.ordinal == other.ordinal
        if type(other) is ZFCSet:
            return self == other.cardinality
        return False

    def __mul__(self, other: "Cardinal"):
        if other.isfinite and self.isfinite:
            return Cardinal(self.ordinal * other.ordinal)
        if other.isfinite and not self.isfinite:
            return Cardinal(self.ordinal, False)
        if not other.isfinite and self.isfinite:
            return Cardinal(other.ordinal, False)
        return Cardinal(max(self.ordinal, other.ordinal), False)

    def __pow__(self, other: "Cardinal | int"):
        if type(other) is int:
            if self.isfinite: return Cardinal(self.ordinal ** other)
            else: return self
        if other.isfinite and self.isfinite:
            return Cardinal(self.ordinal ** other.ordinal)
        if other.isfinite and not self.isfinite:
            return self
        if not other.isfinite and self.isfinite:
            return Cardinal(other.ordinal + 1, False)
        return Cardinal(max(self.ordinal, other.ordinal) + 1, False)

    def __rpow__(self, other: int):
        if not self.isfinite:
            return Cardinal(self.ordinal + 1, False)
        return Cardinal(other ** self.ordinal)

    def __add__(self, other: "Cardinal"):
        if type(other) is int:
            if self.isfinite:
                return Cardinal(self.ordinal + other)
            return self
        if other.isfinite and self.isfinite:
            return Cardinal(self.ordinal + other.ordinal)
        if other.isfinite and not self.isfinite:
            return Cardinal(self.ordinal, False)
        if not other.isfinite and self.isfinite:
            return Cardinal(other.ordinal, False)
        return Cardinal(max(self.ordinal, other.ordinal), False)

    def __radd__(self, other: int):
        if self.isfinite:
            return Cardinal(self.ordinal + other)
        return self

    def __rmul__(self, other: int):
        if self.isfinite:
            return Cardinal(self.ordinal * other)
        return self

    def __ge__(self, other: "Cardinal"):
        if self.isfinite == other.isfinite:
            return self.ordinal >= other.ordinal
        if self.isfinite:
            return False

    def __gt__(self, other: "Cardinal"):
        if self.isfinite == other.isfinite:
            return self.ordinal > other.ordinal
        if self.isfinite:
            return False

    def __le__(self, other: "Cardinal"):
        if self.isfinite == other.isfinite:
            return self.ordinal <= other.ordinal
        if self.isfinite:
            return True

    def __lt__(self, other: "Cardinal"):
        if self.isfinite == other.isfinite:
            return self.ordinal < other.ordinal
        if self.isfinite:
            return True

    def __hash__(self):
        return hash((self.ordinal, self.isfinite))

    def __getitem__(self, key: int):
        return Cardinal(key, self.isfinite)

    def __repr__(self):
        if not self.isfinite: return f'aleph_{self.ordinal}'
        return str(self.ordinal)

class ZFCSet:
    cardinality: Cardinal
    definition: Callable[[Any], bool] | None
    container: frozenset | None

    def __init__(self, *args, definition = lambda x: False, cardinality = Cardinal(0)):
        if args or cardinality == 0:
            self.cardinality = Cardinal(len(args))
            def defin(item: Any) -> bool:
                return item in args
            self.definition = defin
            self.container = frozenset(args)
        else:
            self.cardinality = cardinality
            def defin(item: Any) -> bool:
                return definition(item)
            self.definition = defin
            self.container = None

    def __eq__(self, other: "ZFCSet"): # works only for finite sets
        if type(other) is ZFCSet:
            if other.cardinality.isfinite and self.cardinality.isfinite:
                return self.container == other.container
        return False

    def __iter__(self):
        if self.cardinality.isfinite: return iter(self.container)

    def crossprod(self, other: "ZFCSet"):
        if self.cardinality.isfinite and other.cardinality.isfinite:
            return ZFCSet(tuple(Vector(tup) for tup in product(self.container, other.container)))
        else:
            def defin(item):
                if type(item) is Vector:
                    if item.dim == 2:
                        return item.x in self and item.y in other
                return False
            return ZFCSet(definition=defin, cardinality=(self.cardinality * other.cardinality))

    def __mul__(self, other: "ZFCSet"):
        return self.crossprod(other)

    def __or__(self, other: "ZFCSet"):
        if self.container is not None and other.container is not None:
            return ZFCSet(*(self.container | other.container))
        return ZFCSet(definition=lambda x: (x in self or x in other), cardinality=(self.cardinality + other.cardinality))

    def __and__(self, other: "ZFCSet"):
        if self.container is not None and other.container is not None:
            return ZFCSet(*(self.container & other.container))
        if self.container is not None:
            cont = set()
            for x in self.container:
                if x in other:
                    cont.add(x)
            return ZFCSet(*cont)
        if other.container is not None:
            cont = set()
            for x in other.container:
                if x in self:
                    cont.add(x)
            return ZFCSet(*cont)
        return ZFCSet(definition=lambda x: (x in self and x in other), cardinality=(min(self.cardinality, other.cardinality)))

    def __pow__(self, other: "ZFCSet | int"):
        if type(other) is int:
            return ZFCSet(definition=lambda x: (type(x) is Vector and x.dim == other and all((y in self) for y in x)), cardinality=self.cardinality ** other)
        if isinstance(other, ZFCSet):
            return ZFCSet(definition=lambda x: (type(x) is ZFCFunction), cardinality=(self.cardinality ** other.cardinality))

    def __sub__(self, other: "ZFCSet"):
        if self.container is not None and other.container is not None:
            return ZFCSet(*(self.container - other.container))
        if self.container is not None:
            cont = set()
            for x in self.container:
                if x not in other:
                    cont.add(x)
            return ZFCSet(*cont)
        return ZFCSet(definition=lambda x: (x in self and x not in other), cardinality=(min(self.cardinality, other.cardinality)))

    def __contains__(self, item):
        return self.definition(item)

    def __abs__(self):
        return self.cardinality

    def __bool__(self):
        return self.cardinality > Cardinal()

    def __repr__(self):
        if self.container is not None:
            if self.container == set():
                return r'{}'
            return repr(set(self.container))
        return f'{self.cardinality} ZFC set'

    def __hash__(self):
        return hash((self.container, self.definition, self.cardinality))

class ZFCFunction(ZFCSet):
    rule: Callable[[Any], Any]
    dom: ZFCSet
    range: ZFCSet
    def __init__(self, dom: ZFCSet, rng: ZFCSet, rule: Callable[[Any], Any], name: str):
        self.rule = rule
        self.dom = dom
        self.range = rng
        self.cardinality = dom.cardinality * rng.cardinality
        def defin(item):
            if type(item) is Vector:
                if item.dim == 2:
                    return item.x in self.dom and item.y in self.range and self.rule(item.x) == item.y
            return False
        self.definition = defin
        self.container = None
        self.name = name

    def __add__(self, g: "ZFCFunction"):
        if type(g) is ZFCFunction and self.dom == g.dom and self.range == g.range:
            return ZFCFunction(g.dom, g.range, lambda x: (self(x) + g(x)), f'({self.name} + {g.name})')
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (self(x) + g), f'({self.name} + {g})')
        raise ValueError("Both functions need to have the same domain/range")
    def __mul__(self, g: "ZFCFunction"):
        if type(g) is ZFCFunction and self.dom == g.dom and self.range == g.range:
            return ZFCFunction(g.dom, g.range, lambda x: (self(x) * g(x)), f'({self.name} * {g.name})')
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (self(x) * g), f'({self.name} * {g})')
        raise ValueError("Both functions need to have the same domain/range")
    def __sub__(self, g: "ZFCFunction"):
        if type(g) is ZFCFunction and self.dom == g.dom and self.range == g.range:
            return ZFCFunction(g.dom, g.range, lambda x: (self(x) - g(x)), f'({self.name} - {g.name})')
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (self(x) - g), f'({self.name} - {g})')
        raise ValueError("Both functions need to have the same domain/range")
    def __truediv__(self, g: "ZFCFunction"):
        if type(g) is ZFCFunction and self.dom == g.dom and self.range == g.range:
            return ZFCFunction(g.dom, g.range, lambda x: (self(x) / g(x)), f'({self.name} / {g.name})')
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (self(x) / g), f'({self.name} / {g})')
        raise ValueError("Both functions need to have the same domain/range")
    def __floordiv__(self, g: "ZFCFunction"):
        if type(g) is ZFCFunction and self.dom == g.dom and self.range == g.range:
            return ZFCFunction(g.dom, g.range, lambda x: (self(x) // g(x)), f'({self.name} // {g.name})')
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (self(x) // g), f'({self.name} // {g})')
        raise ValueError("Both functions need to have the same domain/range")
    def __matmul__(self, g: "ZFCFunction"): # (f@g)=f(g())
        if type(g) is not ZFCFunction:
            raise TypeError("Cannot compose non-function on a function")
        return ZFCFunction(g.dom, self.range, lambda x: (self(g(x))), f'({self.name}@{g.name})')

    def __radd__(self, g: "ZFCFunction"):
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (g + self(x)), f'({g} + {self.name})')
        raise ValueError
    def __rmul__(self, g: "ZFCFunction"):
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (g * self(x)), f'({g} * {self.name})')
        raise ValueError
    def __rsub__(self, g: "ZFCFunction"):
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (g - self(x)), f'({g} - {self.name})')
        raise ValueError
    def __rtruediv__(self, g: "ZFCFunction"):
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (g / self(x)), f'({g} / {self.name})')
        raise ValueError
    def __rfloordiv__(self, g: "ZFCFunction"):
        if g in self.range:
            return ZFCFunction(self.dom, self.range, lambda x: (g // self(x)), f'({g} // {self.name})')
        raise ValueError

    def __call__(self, arg):
        return self.rule(arg)

    def __repr__(self):
        return f'{self.name}: {self.dom} -> {self.range}'
