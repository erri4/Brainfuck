from pathlib import Path
import os
import subprocess
import argparse
import sys

'''
case 0b0000: # syscall code value
case 0b0001: # }
case 0b0010: # ptr++
case 0b0011: # mem[ptr]++
case 0b0100: # ptr--
case 0b0101: # add (next HB) HB's in offset to this
case 0b0110: # sub (next HB) HB's in offset to this (this-other)
case 0b0111: # jmp forward to (next HB) HB's in offset
case 0b1000: # {
case 0b1001: # mod (next HB) HB's in offset to this (this%other)
case 0b1010: # int div (next HB) HB's in offset to this (this/other)
case 0b1011: # mul (next HB) HB's in offset to this
case 0b1100: # mem[ptr]--
case 0b1101: # while this enter the block
case 0b1110: # jmp backward to (next HB) HB's in offset
case 0b1111: # if this enter the block
'''

class Token:
    word: str
    value: int | tuple[int, int, int] = None
    def __init__(self, word: str, value: int = None):
        self.word = word
        self.value = value

    def __repr__(self):
        return f'{self.word} {self.value if self.value is not None else '\b'}'

# nuitka --onefile --standalone --follow-imports --windows-console-mode=force ./binar.py
def flter(code: str):
    valid_commands = {'0', '1'}
    return ''.join([char for char in code if char in valid_commands])

def tokenize(script: str):
    i = 0
    tokens = []
    while i + 4 <= len(script):
        match int(script[i: i + 4], 2):
            case 0b0000: # syscall code value
                code = int(script[i + 4: i + 8], 2)
                if code != 0b1011 and code != 0b1100 and code != 0b1101:
                    numbytes = int(script[i + 8: i + 12], 2)
                    bytesstr = '0'
                    for j in range(numbytes):
                        bytesstr += script[i + 12 + j * 4: i + 16 + j * 4]
                    tokens.append(Token('SYSCALL', (code, len(bytesstr) - 1, int(bytesstr, 2))))
                    i += (numbytes + 2) * 4
                elif code == 0b1011:
                    params = script[i + 8: i + 12]
                    i += 4
                    numbytes = int(script[i + 8: i + 12], 2)
                    params += script[i + 8: i + 12]
                    for j in range(numbytes):
                        params += script[i + 12 + j * 4: i + 16 + j * 4]
                    i += (numbytes + 2) * 4
                    tokens.append(Token('SYSCALL', (code, len(params), int(params, 2))))
                elif code == 0b1100:
                    params = ''
                    numbytes = int(script[i + 8: i + 12], 2)
                    params += script[i + 8: i + 12]
                    for j in range(numbytes):
                        params += script[i + 12 + j * 4: i + 16 + j * 4]
                    i += (numbytes + 1) * 4
                    numprms = int(script[i + 8: i + 12], 2)
                    params += script[i + 8: i + 12]
                    for j in range(numprms):
                        params += script[i + 12 + j * 4: i + 16 + j * 4]
                    i += (numprms + 2) * 4
                    tokens.append(Token('SYSCALL', (code, len(params), int(params, 2))))
                elif code == 0b1101:
                    op = script[i + 8 : i + 12]
                    sign = int(script[i + 12])
                    numbytes = int(script[i + 13: i + 16], 2)
                    i += 8
                    if numbytes == 0: tokens.append(Token('SYSCALL', (code, 4, int(op, 2))))
                    else:
                        bytesstr = ''
                        for j in range(numbytes):
                            bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                        tokens.append(Token('SYSCALL', (code, len(bytesstr) + 5, int(op + bytesstr, 2) * 2 + sign)))
                    i += (numbytes + 1) * 4
            case 0b0001: # }
                tokens.append(Token('BR_CLOSE'))
            case 0b0010: # ptr++
                tokens.append(Token('FORWARD'))
            case 0b0011: # mem[ptr]++
                tokens.append(Token('INC'))
            case 0b0100: # ptr--
                tokens.append(Token('BACKWARD'))
            case 0b0101: # add (next HB) HB's in offset to this
                sign = int(script[i + 4])
                numbytes = int(script[i + 5: i + 8], 2)
                if numbytes == 0: tokens.append(Token('ADD', 0))
                else:
                    bytesstr = ''
                    for j in range(numbytes):
                        bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                    tokens.append(Token('ADD', int(bytesstr, 2) * 2 + sign))
                i += (numbytes + 1) * 4
            case 0b0110: # substract (next HB) HB's in offset to this (this-other)
                sign = int(script[i + 4])
                numbytes = int(script[i + 5: i + 8], 2)
                if numbytes == 0: tokens.append(Token('SUB', 0))
                else:
                    bytesstr = ''
                    for j in range(numbytes):
                        bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                    tokens.append(Token('SUB', int(bytesstr, 2) * 2 + sign))
                i += (numbytes + 1) * 4
            case 0b0111: # jmp forward to (next HB) HB's in offset
                sign = int(script[i + 4])
                numbytes = int(script[i + 5: i + 8], 2)
                if numbytes == 0: tokens.append(Token('PTR_FOR', 0))
                else:
                    bytesstr = ''
                    for j in range(numbytes):
                        bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                    tokens.append(Token('PTR_FOR', int(bytesstr, 2) * 2 + sign))
                i += (numbytes + 1) * 4
            case 0b1000: # {
                tokens.append(Token('BR_OPEN'))
            case 0b1001: # mod (next HB) HB's in offset to this (this%other)
                sign = int(script[i + 4])
                numbytes = int(script[i + 5: i + 8], 2)
                if numbytes == 0: tokens.append(Token('MOD', 0))
                else:
                    bytesstr = ''
                    for j in range(numbytes):
                        bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                    tokens.append(Token('MOD', int(bytesstr, 2) * 2 + sign))
                i += (numbytes + 1) * 4
            case 0b1010: # int div (next HB) HB's in offset to this (this/other)
                sign = int(script[i + 4])
                numbytes = int(script[i + 5: i + 8], 2)
                if numbytes == 0: tokens.append(Token('DIV', 0))
                else:
                    bytesstr = ''
                    for j in range(numbytes):
                        bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                    tokens.append(Token('DIV', int(bytesstr, 2) * 2 + sign))
                i += (numbytes + 1) * 4
            case 0b1011: # mul (next HB) HB's in offset to this
                sign = int(script[i + 4])
                numbytes = int(script[i + 5: i + 8], 2)
                if numbytes == 0: tokens.append(Token('MUL', 0))
                else:
                    bytesstr = ''
                    for j in range(numbytes):
                        bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                    tokens.append(Token('MUL', int(bytesstr, 2) * 2 + sign))
                i += (numbytes + 1) * 4
            case 0b1100: # mem[ptr]--
                tokens.append(Token('DEC'))
            case 0b1101: # while this enter the block
                tokens.append(Token('WHILE'))
            case 0b1110: # read/write const ptr
                rw = int(script[i + 4])
                numbytes = int(script[i + 5: i + 8], 2)
                if numbytes == 0: tokens.append(Token('RW_PTR', rw))
                else:
                    bytesstr = ''
                    for j in range(numbytes):
                        bytesstr += script[i + 8 + j * 4: i + 12 + j * 4]
                    tokens.append(Token('RW_PTR', int(bytesstr, 2) * 2 + rw))
                i += (numbytes + 1) * 4
            case 0b1111: # if this enter the block
                tokens.append(Token('IF'))
        i += 4
    return tokens

def optimize(script: list[Token]):
    return script

def compress(file: str) -> str:
    with open(file) as f:
        scr = ''
        i = 0
        script = flter(f.read())
        while i + 8 <= len(script):
            scr += chr(int(script[i : i + 8], 2))
            i += 8
        if i + 4 == len(script):
            scr += chr(int(script[i:], 2)) + chr(1)
        else:
            scr += chr(0)
    return scr

def decompress(file: str) -> str:
    with open(file, 'rb') as f:
        scr = ''
        i = 0
        script = f.read().decode()
        mod = ord(script[-1])
        while i < len(script) - 1:
            bits = bin(ord(script[i]))[2:]
            if i < len(script) - 2:
                bits = '0' * (8 - len(bits)) + bits
            else:
                if mod: bits = '0' * (4 - len(bits)) + bits
                else: bits = '0' * (8 - len(bits)) + bits
            scr += bits
            i += 1
    return scr

def main():
    parser = argparse.ArgumentParser(description="Binar interpreter/compiler.")
    parser.add_argument("script", help="Path to the Binar script to run")

    parser.add_argument("--compile", '-c', action="store_true", help="Compile program")
    parser.add_argument("--compress", '-co', action="store_true", help="Compress program")
    parser.add_argument("--decompress", '-d', action="store_true", help="Compress program")
    parser.add_argument("--debug", action="store_true", help="Debug")

    args = parser.parse_args()

    try:
        if args.script.endswith('.cb'):
            script = optimize(tokenize(flter(decompress(args.script))))
        else:
            with open(args.script) as f:
                script = optimize(tokenize(flter(f.read())))
    except UnicodeDecodeError:
        script = optimize(tokenize(flter(decompress(args.script))))
    if args.compile:
        compile_(script, args.debug, args.script)
    elif args.compress:
        with open(Path(args.script).with_suffix(".cb"), 'wb') as f:
            f.write(compress(args.script).encode())
    elif args.decompress:
        with open(Path(args.script).with_suffix(".binar"), 'w') as f:
            f.write(decompress(args.script))
    else:
        interpret(script, args.debug)


def compile_(script: list[Token], debug: bool = False, file: str = ''):
    def compile_to_c(tokens: list[Token]):
        pass
    
    c_output = compile_to_c(script)
    with open(os.path.basename(os.path.splitext(file)[0]) + '.c',"w") as f:
        f.write(c_output)
    subprocess.run(f'gcc -o {os.path.basename(os.path.splitext(file)[0])} {os.path.basename(os.path.splitext(file)[0]) + '.c'}')
    os.remove(os.path.basename(os.path.splitext(file)[0]) + '.c')

ptr = 0
mem = [0]
stack = []
functions = {}
scopes: list[list[Token]] = []

def syscall(code: int, length: int, value: int, **qwargs):
    global mem, ptr, stack, functions, scopes
    binary = bin(value)[2:]
    binary = '0' * (length - len(binary)) + binary
    match code:
        case 0b0000:
            ch = sys.stdin.read(1)
            if ch == "":
                mem[ptr] = 0
            else:
                mem[ptr] = ord(ch[0])
        case 0b0001:
            print(chr(mem[ptr]), end='')
        case 0b0010:
            ptr = value
            extend(ptr)
        case 0b0011:
            mem[ptr] = ptr
        case 0b0100:
            mem[ptr] = stack[-1][value]
        case 0b0101:
            mem[ptr] += value
        case 0b0110:
            mem[ptr] *= value
        case 0b0111:
            mem[ptr] -= value
        case 0b1000:
            mem[ptr] //= value
        case 0b1001:
            mem[ptr] %= value
        case 0b1010:
            mem[ptr] = mem[mem[ptr]]
        case 0b1011: # def
            params = int(binary[:4], 2)
            binary = binary[4:]
            namelen = int(binary[:4], 2)
            binary = binary[4:]
            name = int(binary[:4 * namelen], 2)
            code = []
            start: int = qwargs['i']
            script = scopes[-1]
            while script[start].word != 'BR_OPEN': start += 1
            end = start
            scope = 1
            while scope > 0:
                end += 1
                if script[end].word == 'BR_CLOSE': scope -= 1
                if script[end].word == 'BE_OPEN': scope += 1
            code = script[start : end + 1]
            functions[name] = (params, code)
            del script[start : end + 1]
        case 0b1100: # call
            namelen = int(binary[:4], 2)
            binary = binary[4:]
            name = int(binary[:4 * namelen], 2)
            binary = binary[4 * namelen:]
            params = []
            for _ in range(functions[name][0]):
                params.append(int(binary[:4], 2))
                binary = binary[4:]
            stack.append(params)
            interpret(functions[name][1])
        case 0b1101:
            op = (int(binary[0]), int(binary[1]), int(binary[2]), int(binary[3]))
            value, sign = int(binary[4:], 2) // 2, int(binary[4:], 2) % 2
            sign = sign * 2 - 1
            mem[ptr] = logicop(op, mem[ptr], mem[ptr + sign * value])
        case 0b1110:
            op = (int(binary[0]), int(binary[1]), int(binary[2]), int(binary[3]))
            mem[ptr] = logicop(op, mem[ptr], int(binary[4:], 2))
        case 0b1111:
            try:
                interpret(tokenize(decompress(dot() + '/stdb.cb')))
            except FileNotFoundError:
                with open(dot() + '/stdb.binar') as stdb:
                    interpret(tokenize(flter(stdb.read())))

def logicop(op: tuple[int, int, int, int], a: int, b: int):
    operator = lambda x, y: op[int(str(x) + str(y), 2)]
    # a b
    # 0 0
    # 0 1
    # 1 0
    # 1 1
    aL = list(bin(a)[2:])
    bL = list(bin(b)[2:])
    bL = (['0'] * (max(len(bL), len(aL)) - len(bL))) + bL
    aL = (['0'] * (max(len(bL), len(aL)) - len(aL))) + aL
    return int(''.join([str(operator(x, y)) for x, y in zip(aL, bL)]), 2)

def extend(n: int = None):
    global mem, ptr
    if n is None: n = ptr
    mem.extend([0] * (n - len(mem) + 1))

def dot():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def interpret(script: list[Token], debug: bool = False):
    global mem, ptr, scopes
    i = 0
    scopes.append(script)
    # print(script)
    while i < len(script):
        match script[i].word:
            case 'INC':
                mem[ptr] += 1
            case 'DEC':
                mem[ptr] -= 1
            case 'FORWARD':
                ptr += 1
                extend(ptr)
            case 'BACKWARD':
                ptr -= 1
            case 'BR_OPEN': pass
            case 'BR_CLOSE': pass
            case 'IF':
                start = i
                while script[start].word != 'BR_OPEN': start += 1
                end = start
                scope = 1
                while scope > 0:
                    end += 1
                    if script[end].word == 'BR_CLOSE': scope -= 1
                    if script[end].word == 'BE_OPEN': scope += 1
                if mem[ptr]:
                    interpret(script[start:end + 1])
                i = end
            case 'WHILE':
                start = i
                while script[start].word != 'BR_OPEN': start += 1
                end = start
                scope = 1
                while scope > 0:
                    end += 1
                    if script[end].word == 'BR_CLOSE': scope -= 1
                    if script[end].word == 'BE_OPEN': scope += 1
                while mem[ptr]:
                    interpret(script[start:end + 1])
                i = end
            case 'PTR_FOR':
                value, sign = script[i].value // 2, script[i].value % 2
                sign = sign * 2 - 1
                ptr += sign * value
                extend(ptr)
            case 'RW_PTR':
                value, rw = script[i].value // 2, script[i].value % 2
                extend(value)
                if rw == 0: mem[ptr] = mem[value]
                else: mem[value] = mem[ptr]
            case 'ADD':
                value, sign = script[i].value // 2, script[i].value % 2
                sign = sign * 2 - 1
                mem[ptr] += mem[ptr + sign * value]
            case 'SUB':
                value, sign = script[i].value // 2, script[i].value % 2
                sign = sign * 2 - 1
                mem[ptr] -= mem[ptr + sign * value]
            case 'MUL':
                value, sign = script[i].value // 2, script[i].value % 2
                sign = sign * 2 - 1
                mem[ptr] *= mem[ptr + sign * value]
            case 'DIV':
                value, sign = script[i].value // 2, script[i].value % 2
                sign = sign * 2 - 1
                mem[ptr] //= mem[ptr + sign * value]
            case 'MOD':
                value, sign = script[i].value // 2, script[i].value % 2
                sign = sign * 2 - 1
                mem[ptr] %= mem[ptr + sign * value]
            case 'SYSCALL':
                syscall(script[i].value[0], script[i].value[1], script[i].value[2], i=i)
        i += 1
        mem[ptr] %= 256
    scopes.pop()

if __name__ == '__main__':
    main()