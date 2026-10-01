from ZFCSet import ZFCSet, ZFCFunction, Cardinal
from Rational import Rational as Rat
from Vector import Vector
import math
import argparse
import operator as oper
import itertools
import re
import ast

'''
TODO:
complex
some builtins
'''

class Operator:
    start: "list[Token] | None" = None
    end: "list[Token] | None" = None
    operator = None

    def __init__(self, op, start = None, end = None):
        self.operator = op
        self.start = start
        self.end = end

    def __pow__(self, other):
        self.end = other
        return self

    def __getitem__(self, key):
        self.start = key
        return self

    def __call__(self, expr):
        res = None
        ex = []
        for x in expr: ex += x
        if self.end:
            evaluate(self.start)
            while not evaluate(self.end):
                if res is None: res = evaluate(ex)
                else: res = self.operator(res, evaluate(ex))
            return res
        while self.start[0].word == 'brackets':
            self.start[0] = self.start[0].value[0]
        if self.start[0].word == 'in':
            set_ = evaluate(self.start[0].value[1])
            if set_.cardinality.isfinite:
                if self.start[0].value[0][0].word == 'word':
                    for el in set_:
                        evaluate([Token('assignvar', {'var': self.start[0].value[0][0].value, 'value': [Token('const', el)]})])
                        if res is None: res = evaluate(ex)
                        else: res = self.operator(res, evaluate(ex))
                    return res
            else:
                raise TypeError('Cannot loop on an infinite set')
        else:
            raise TypeError('Cannot loop without a stopping condition')

class Operator_getter:
    operator = None
    def __init__(self, op):
        self.operator = op

    def __getitem__(self, key):
        return Operator(self.operator, start=key)

    def __pow__(self, key):
        return Operator(self.operator, end=key)

EMPTYSET = ZFCSet()
ALEPH = Cardinal(1, False)
Cardinals = ZFCSet(definition=lambda x: (type(x) is Cardinal), cardinality=ALEPH[0])
Cardinals.__class__ = type("Cardinalsset", (ZFCSet,), {'__repr__': lambda x: 'Cardinals', '__str__': lambda x: 'Cardinals'})
N = ZFCSet(definition=lambda x: (type(x) is int and x >= 0), cardinality=ALEPH[0])
N.__class__ = type("Nset", (ZFCSet,), {'__repr__': lambda x: 'N', '__str__': lambda x: 'N'})
Z = ZFCSet(definition=lambda x: (type(x) is int), cardinality=ALEPH[0])
Z.__class__ = type("Zset", (ZFCSet,), {'__repr__': lambda x: 'Z', '__str__': lambda x: 'Z'})
Q = ZFCSet(definition=lambda x: (type(x) is int or type(x) is Rat or type(x) is float), cardinality=ALEPH[0])
Q.__class__ = type("Qset", (ZFCSet,), {'__repr__': lambda x: 'Q', '__str__': lambda x: 'Q'})
Set = ZFCSet(definition=lambda x: True, cardinality=Cardinal(float('inf'), False)) # everything is a set
Set.__class__ = type("Setset", (ZFCSet,), {'__repr__': lambda x: 'Set', '__str__': lambda x: 'Set'})
Functions = ZFCSet(definition=lambda x: (type(x) is ZFCFunction), cardinality=Cardinal(float('inf'), False))
Functions.__class__ = type("Functionsset", (ZFCSet,), {'__repr__': lambda x: 'Functions', '__str__': lambda x: 'Functions'})
Strings = ZFCSet(definition=lambda x: (type(x) is str), cardinality=ALEPH[0]) # finite strings so equiv to algebric numbers => aleph_0
Strings.__class__ = type("Stringsset", (ZFCSet,), {'__repr__': lambda x: 'Strings', '__str__': lambda x: 'Strings'})
Bool = ZFCSet(True, False)
Bool.__class__ = type("Boolset", (ZFCSet,), {'__repr__': lambda x: 'Bool', '__str__': lambda x: 'Bool'})
Sigma = Operator_getter(oper.add)
Pi = Operator_getter(oper.mul)
Cup = Operator_getter(oper.or_)
Cap = Operator_getter(oper.and_)

def Rational(a, b):
    if a in Q and b in Q: return Rat(a, b)
    return a / b

def P(sets: list[ZFCSet]) -> ZFCSet:
    s = sets[0]
    if s.cardinality.isfinite:
        subsets = set()
        for x in itertools.chain.from_iterable(itertools.combinations(list(s.container), r) for r in range(abs(s).ordinal + 1)):
            subsets.add(ZFCSet(*x))
        return ZFCSet(*subsets)

    def defin(subset: ZFCSet) -> bool:
        if subset.cardinality.isfinite:
            return all(x in s for x in subset)
        return False # idk how to check for infinite sets.
    return ZFCSet(definition=defin, cardinality=2**s.cardinality)

type Tokenvaluetype = tuple[list[Token], ...] | str | dict[str, str | list[Token]] | tuple[list[Token], list[Token]] | tuple[Token, list[Token]]

class Token:
    word: str
    value: Tokenvaluetype = None
    def __init__(self, word: str, value: Tokenvaluetype = None):
        self.word = word
        self.value = value

    def __repr__(self):
        return f'{self.word} {self.value if self.value is not None else '\b'}'

def num_const(s: str) -> Rat | int | bool:
    try:
        node = ast.parse(s.strip(), mode="eval").body
    except SyntaxError:
        return
    if isinstance(node, ast.Constant) and type(node.value) is int:
            return Rat.from_float(node.value)
    if isinstance(node, ast.Constant) and type(node.value) is bool:
                return node.value
    if isinstance(node, ast.Constant) and isinstance(node.value, float):
        return Rat.from_float(node.value)

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        operand = num_const(ast.unparse(node.operand))
        if operand: return -operand
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv)):
        right = num_const(ast.unparse(node.right))
        left = num_const(ast.unparse(node.left))
        if left and right:
            return Rational(left, right)

def arith(s: str) -> tuple[str, str, str] | None:
    names = {
        '+': 'add',
        '-': 'sub',
        '*': 'mul',
        '/': 'div',
        '^': 'pow',
        '&': 'and',
        '%': 'mod',
        '@': 'comp',
        '>': 'gt',
        '<': 'lt',
        '=': 'eq',
    }
    order = {
        '+': 4,
        '-': 4,
        '*': 3,
        '/': 3,
        '^': 1,
        '&': 2,
        '@': 2,
        '%': 3,
        '<': 5,
        '>': 5,
        '=': 5,
    }
    closing = {
        '{': '}',
        '[': ']',
        '(': ')',
        '|': '|',
    }
    substr = ''
    op = ''
    res = []
    stk = []
    for char in s:
        if char in closing: stk.append(closing[char])
        if stk and char == stk[-1]: stk.pop()
        if len(stk) == 0 and char in names:
            if op == '':
                op = char
                res.append(substr.strip())
                substr = ''
                continue
            if order[op] < order[char]:
                res[-1] += op + substr.strip()
                op = char
                substr = ''
                continue
        substr += char
    res.append(substr.strip())
    if len(res) == 2:
        return (names[op], res[0], res[1])

def isclosed(s: str) -> bool:
    closing = {
        '{': '}',
        '[': ']',
        '(': ')',
        '|': '|',
    }
    stk = []
    for char in s:
        if char in closing: stk.append(closing[char])
        if stk and char == stk[-1]: stk.pop()
    return len(stk) == 0

def extractargs(line: str, funcname: str):
    rawargs = line[len(funcname):-1].strip()
    rawargs = rawargs[rawargs.find('(')+1:].strip()
    if rawargs == "":
        return []
    splitted = smrtsplt(rawargs, ",")
    if funcname == 'swap': return splitted
    return [tokenizer(arg.strip()) for arg in splitted]

def parse_function_call(expr: str):
    if not is_function_call(expr): return None
    splitted = smrtsplt(expr, "(")
    prefix = "(".join(splitted[:-1])
    args = extractargs(expr, prefix)
    return {'func': tokenizer(prefix), 'args': args}

def is_function_call(expr: str):
    expr = expr.strip()
    if "(" not in expr:
        return False
    splitted = smrtsplt(expr, "(")
    prefix = "(".join(splitted[:-1])
    if not tokenizer(prefix, mode='check'):
        return False
    rest = splitted[-1]
    if not prefix.strip():
        return False
    if not rest.endswith(")"):
        return False
    
    return True

def smrtsplt(s: str, deli: str) -> list[str]:
    closing = {
        '{': '}',
        '[': ']',
        '(': ')',
        '|': '|',
    }
    substr = ''
    res = []
    stk = []
    i = 0
    while i < len(s):
        char = s[i]
        substr += char
        if len(stk) == 0 and s[i:i+len(deli)] == deli:
            res.append(substr[:-1].strip())
            substr = ''
            i += len(deli) - 1
        if char in closing: stk.append(closing[char])
        if stk and char == stk[-1]: stk.pop()
        i += 1
    res.append(substr.strip())
    return res

def tokenizer(script: str, mode: str = 'eval') -> list[Token]:
    lines = script.replace('\n', '').split(';')
    code: list[Token] = []
    for line in lines:
        line = line.strip()
        if line == '' or line.startswith('//'): continue
        arithmetic = arith(line)
        func = parse_function_call(line)
        const = num_const(line)
        in_ = smrtsplt(line, ' in ')
        le1 = smrtsplt(line, '<=')
        le2 = smrtsplt(line, '=<')
        ge = smrtsplt(line, '>=')
        or_ = smrtsplt(line, ' or ')
        sp_ = smrtsplt(line, '_')
        tup = smrtsplt(line[1:-1], ',')
        assign = smrtsplt(line, ':=')
        if line == 'True':
            code.append(Token('const', True))
        elif line == 'False':
            code.append(Token('const', False))
        elif not line[0].isdigit() and line.isalnum():
            code.append(Token('word', line))
        elif line.startswith('let '):
            regex = r"^let\s+([a-zA-Z_]\w*)\s*(?:in\s+(.+)|:\s*(.+?)\s*->\s*(.+))$"
            match = re.search(regex, line.strip())
            if not match:
                continue
            var, in_expr, domain, codomain = match.groups()
            if in_expr is not None:
                code.append(Token('letvar', {"var": var, "set": tokenizer(in_expr.strip())}))
            else:
                code.append(Token('letfunc', {"func": var, "dom": tokenizer(domain.strip()), "range": tokenizer(codomain.strip())}))
        elif line.startswith('lambda '):
            args = smrtsplt(line[len('lambda')+1:line.find('.')].strip(), ',')
            args = [tokenizer(arg) for arg in args]
            value = tokenizer(line[line.find('.')+1:].strip())
            code.append(Token('lambda', {'value': value, 'args': args}))
        elif line.startswith('cases{'):
            cases = line[len('cases{'):line.rfind('}')]
            cses = []
            el = None
            splt = smrtsplt(cases, ',')
            for cond in splt:
                cond = cond.strip()
                splitted = smrtsplt(cond, ' if ')
                if len(splitted) > 1:
                    cses.append((tokenizer(splitted[0]), tokenizer(splitted[1])))
                if ' else' in cond:
                    el = tokenizer(cond[:cond.rfind(' else')])
            code.append(Token('cases', (cses, el)))
        elif len(assign) > 1:
            name, expr = assign
            name = name.strip()
            expr = expr.strip()
            f = parse_function_call(name)
            if not name[0].isdigit() and name.isalnum():
                code.append(Token('assignvar', {'var': name, 'value': tokenizer(expr)}))
            elif '_' in name:
                idx = name[name.find('_')+1:]
                code.append(Token('assignidx', {'var': name[:name.find('_')], 'idx': tokenizer(idx), 'value': tokenizer(expr)}))
            elif f:
                code.append(Token('assignfunc', {'func': f['func'], 'value': tokenizer(expr), 'args': f['args']}))
        elif len(in_) > 1:
            code.append(Token('in', (tokenizer(in_[0].strip()), tokenizer(' in '.join(in_[1:]).strip()))))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif len(or_) > 1:
            code.append(Token('or', (tokenizer(or_[0].strip()), tokenizer(' or '.join(or_[1:]).strip()))))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif len(le1) > 1:
            code.append(Token('le', (tokenizer(le1[0].strip()), tokenizer(' <= '.join(le1[1:]).strip()))))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif len(le2) > 1:
            code.append(Token('le', (tokenizer(le2[0].strip()), tokenizer(' <= '.join(le2[1:]).strip()))))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif len(ge) > 1:
            code.append(Token('ge', (tokenizer(ge[0].strip()), tokenizer(' >= '.join(ge[1:]).strip()))))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif func:
            code.append(Token('call', func))
        elif const is not None:
            code.append(Token('const', const))
        elif arithmetic:
            code.append(Token(arithmetic[0], (tokenizer(arithmetic[1]), tokenizer(arithmetic[2]))))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif len(sp_) > 1:
            code.append(Token('idx', (tokenizer(sp_[0]), tokenizer('_'.join(sp_[1:])))))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif line[0] == '"' and line[-1] == '"' and '"' not in line[1:-1]:
            code.append(Token('string', line[1:-1]))
        elif line[0] == '(' and line[-1] == ')' and len(tup) > 1:
            code.append(Token('tuple', tuple(tokenizer(x.strip()) for x in tup)))
            if mode == 'check':
                if any(x == [] for x in code[-1].value): code.append(False)
        elif line[0] == '[' and line[-1] == ']':
            code.append(Token('iverson', tokenizer(line[1:-1])))
        elif line[0] == '(' and line[-1] == ')':
            code.append(Token('brackets', tokenizer(line[1:-1])))
        elif line[0] == '|' and line[-1] == '|':
            code.append(Token('abs', tokenizer(line[1:-1])))
        elif line[0] == '{' and line[-1] == '}':
            line = line[1:-1]
            if '|' in line:
                tok = None
                try:
                    tok = tokenizer(line[:line.find('|')])[0]
                except Exception: pass
                if tok is not None and tok.word == 'in' and tok.value[0][0].word == 'word':
                    code.append(Token('infset', (tok, tokenizer(line[line.find('|')+1:]))))
                    continue
            code.append(Token('finset', [tokenizer(el.strip())[0] for el in smrtsplt(line, ',')]))
        else:
            if mode == 'check': return False
            raise SyntaxError(line + '\nHave you forgotten a semicolon?')
    if mode == 'eval':
        return code
    elif mode == 'check':
        return not any(x is False for x in code)

def prnt(x: list[str] = ['']):
    if x: print(x[0])
    else: print()

def log2(x: list[int]):
    if x[0] <= 1: return 0
    return 1 + log2([x[0] // 2])

def dom(f: list[ZFCFunction]) -> ZFCSet:
    return f[0].dom

def rng(f: list[ZFCFunction]) -> ZFCSet:
    return f[0].range

def divs(x: list[int]):
    n = x[0]
    divisors = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
    return ZFCSet(*divisors)

env: list[dict[str, ZFCFunction | ZFCSet | str | int | Rat | float | Cardinal]] = [{"EMPTYSET": EMPTYSET, "ALEPH": ALEPH, 'N': N, 'Z': Z, 'Q': Q, 'Set': Set, 'Strings': Strings, 'Bool': Bool, 'Cardinals': Cardinals, 'print': ZFCFunction(Strings, EMPTYSET, prnt, 'print'), 'input': ZFCFunction(EMPTYSET, Strings, lambda x: input(), 'input'), 'P': P, 'Sigma': Sigma, 'Pi': Pi, 'Cap': Cap, 'Cup': Cup, 'nullVector': ZFCFunction(N, Q**3, lambda x: (Vector.nullVector(x[0])), 'nullVector'), 'floor': ZFCFunction(Q, Z, lambda x: math.floor(x[0]), 'floor'), 'log2': ZFCFunction(Q, N, log2, 'log2'), 'int': ZFCFunction(Strings, Z, (lambda x: int(x[0])), 'int'), 'gcd': ZFCFunction(N, N, lambda x: math.gcd(x[0], x[1]), 'gcd'), 'divs': ZFCFunction(N, Set, divs, 'divs'), 'dom': ZFCFunction(Functions, Set, dom, 'dom'), 'range': ZFCFunction(Functions, Set, rng, 'range')}]
pending = {}

def evaluate(code: list[Token]) -> Vector | Rat | ZFCSet | str | ZFCFunction | Operator | Operator_getter:
    i = 0
    ret = None
    while i < len(code):
        word, value = code[i].word, code[i].value
        match word:
            case 'word':
                if value in env[-1]:
                    ret = env[-1][value]
                elif value in env[0]:
                    ret = env[0][value]
                else:
                    raise NameError(f'Unknown word "{value}"\nDid you forget to initialize a value?')
            case 'letvar':
                s = evaluate(value['set'])
                pending[value['var']] = (s, (EMPTYSET, s))
                ret = s
            case 'letfunc':
                rng = evaluate(value['range'])
                dom = evaluate(value['dom'])
                pending[value['func']] = (rng ** dom, (dom, rng))
                ret = rng ** dom
            case 'assignvar':
                val = evaluate(value['value'])
                pend = pending.get(value['var'], None)
                if pend is not None:
                    if val not in pending[value['var']][0]:
                        raise TypeError(f"{value['var']} must belong to {pending[value['var']]} by definition")
                    env[-1][value['var']] = val
                    del pending[value['var']]
                    ret = val
                elif value['var'] in env[-1]:
                    env[-1][value['var']] = val
                    ret = val
                elif value['var'] in env[0]:
                    env[0][value['var']] = val
                    ret = val
                else:
                    raise TypeError(f'Unknown word "{value["var"]}": type was not previously declared')
            case 'assignidx':
                idx = evaluate(value['idx'])
                if value['var'] in env[-1]:
                    env[-1][value['var']][idx] = evaluate(value['value'])
                    ret = env[-1][value['var']][idx]
                elif value['var'] in env[0]:
                    env[0][value['var']][idx] = evaluate(value['value'])
                    ret = env[0][value['var']][idx]
                else:
                    raise NameError(f'Unknown word "{value['var']}": not declared')
            case 'assignfunc':
                pend = pending.get(value['func'][0].value, None)
                if pend is not None:
                    def rule(params: list, val: list[Token]=value['value'], args: list[list[Token]] = value['args']):
                        env.append({})
                        if type(params) != list: params = [params]
                        for i in range(len(params)):
                            env[-1][args[i][0].value] = params[i]
                        r = evaluate(val)
                        env.pop()
                        return r
                    env[-1][value['func'][0].value] = ZFCFunction(pend[1][0], pend[1][1], rule, value['func'][0].value)
                    del pending[value['func'][0].value]
                    ret = env[-1][value['func'][0].value]
                else:
                    raise TypeError(f'Unknown word "{value["var"]}": type was not previously declared')
            case 'string':
                ret = value
            case 'lambda':
                def rule(params: list, val: list[Token]=value['value'], args: list[list[Token]] = value['args']):
                    env.append({})
                    for i in range(len(params)):
                        env[-1][args[i][0].value] = params[i]
                    r = evaluate(val)
                    env.pop()
                    return r
                ret = ZFCFunction(Set, Set, rule, 'lambda')
            case 'const':
                ret = value
            case 'cases':
                found = False
                for case in value[0]:
                    if evaluate(case[1]):
                        ret = evaluate(case[0])
                        found = True
                        break
                if not found and value[1] is not None:
                    ret = evaluate(value[1])
            case 'call':
                func = evaluate(value['func'])
                if type(func) is Operator:
                    ret = func(value['args'])
                else:
                    args = [evaluate(arg) for arg in value['args']]
                    ret = func(args)
            case 'add':
                ret = evaluate(value[0]) + evaluate(value[1])
            case 'mod':
                ret = evaluate(value[0]) % evaluate(value[1])
            case 'comp':
                ret = evaluate(value[0]) @ evaluate(value[1])
            case 'sub':
                ret = evaluate(value[0]) - evaluate(value[1])
            case 'mul':
                ret = evaluate(value[0]) * evaluate(value[1])
            case 'div':
                val1 = evaluate(value[0])
                val2 = evaluate(value[1])
                if type(val1) is ZFCFunction:
                    if type(val2) is ZFCFunction and val1.dom == val2.dom and val1.range == val2.range:
                        return ZFCFunction(val2.dom, val2.range, lambda x: Rational(val1(x), val2(x)), f'({val1.name} / {val2.name})')
                    if val2 in val1.range:
                        return ZFCFunction(val1.dom, val1.range, lambda x: Rational(val1(x), val2), f'({val1.name} / {val2})')
                    raise ValueError("Both functions need to have the same domain/range")
                if type(val2) is ZFCFunction:
                    if val1 in val2.range:
                        return ZFCFunction(val2.dom, val2.range, lambda x: Rational(val1, val2(x)), f'({val1} / {val2.name})')
                if type(val1) is int or type(val2) is int:
                    try:
                        ret = Rational(val1, val2)
                    except TypeError:
                        ret = val1 / val2
                else:
                    ret = val1 / val2
            case 'pow':
                obj = evaluate(value[0])
                if type(obj) is Operator_getter or type(obj) is Operator:
                    ret = obj ** value[1]
                else:
                    ret = obj ** evaluate(value[1])
            case 'and':
                ret = evaluate(value[0]) & evaluate(value[1])
            case 'or':
                ret = evaluate(value[0]) | evaluate(value[1])
            case 'in':
                ret = evaluate(value[0]) in evaluate(value[1])
            case 'le':
                ret = evaluate(value[0]) <= evaluate(value[1])
            case 'ge':
                ret = evaluate(value[0]) >= evaluate(value[1])
            case 'lt':
                ret = evaluate(value[0]) < evaluate(value[1])
            case 'gt':
                ret = evaluate(value[0]) > evaluate(value[1])
            case 'eq':
                ret = evaluate(value[0]) == evaluate(value[1])
            case 'iverson':
                ret = int(evaluate(value))
            case 'brackets':
                ret = evaluate(value)
            case 'abs':
                ret = abs(evaluate(value))
            case 'idx':
                obj = evaluate(value[0])
                if type(obj) is Operator_getter or type(obj) is Operator:
                    ret = obj[value[1]]
                else:
                    ret = obj[evaluate(value[1])]
            case 'tuple':
                ret = Vector(tuple(evaluate(x) for x in value))
            case 'finset':
                ret = ZFCSet(*[evaluate([x]) for x in value])
            case 'infset':
                U = evaluate(value[0].value[1])
                def definition(param: int, val: list[Token]=value[1], arg: list[Token] = value[0].value[0], Uni=U):
                    env.append({})
                    env[-1][arg[0].value] = param
                    r = evaluate(val)
                    env.pop()
                    return (param in Uni) and bool(r)
                ret = ZFCSet(definition=definition, cardinality=U.cardinality)
        i += 1
    return ret

def main():
    parser = argparse.ArgumentParser(description="ZFC interpreter.")
    parser.add_argument("script", help="Path to the ZFC script to run")

    args = parser.parse_args()

    with open(args.script) as f:
        script = tokenizer(f.read())
    evaluate(script)

if __name__ == '__main__':
    main()