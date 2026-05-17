from typing import Literal
import argparse
import random
import sys

class Stack[_T](list):
    def pop(self) -> _T:
        try:
            return super().pop()
        except IndexError:
            return 0

def main():
    parser = argparse.ArgumentParser(description="Brainfuck interpreter/compiler.")
    parser.add_argument("script", help="Path to the Brainfuck script to run")

    parser.add_argument("--compile", '-c', action="store_true", help="Compile program")
    parser.add_argument("--debug", '-d', action="store_true", help="Debug")

    args = parser.parse_args()

    with open(args.script) as f:
        script = [list(x) for x in f.read().splitlines()]
    mx = 0
    for i in range(len(script)):
        if len(script[i]) > len(script[mx]):
            mx = i
    for i in range(len(script)):
        script[i].extend([' ']*(len(script[mx]) - len(script[i])))
    script = [[script[y][x] for y in range(len(script))] for x in range(len(script[0]))]
    if args.compile:
        compile_(script, args.debug, args.script)
    else:
        interpret(script, args.debug, args.script)


def compile_(script: list[list[str]], debug: bool = False, file: str = ''):
    pass

def move(x: int, y: int, dir: Literal['>', '<', 'v', '^']):
    match dir:
        case '>':
            return x+1, y
        case '<':
            return x-1, y
        case 'v':
            return x, y+1
        case '^':
            return x, y-1

def interpret(script: list[list[str]], debug: bool = False, file: str = ''):
    x: int = 0
    y: int = 0
    dir: Literal['>', '<', 'v', '^'] = '>'
    stack: Stack[int] = Stack()
    string_mode: bool = False
    try:
        while script[x][y] != '@':
            x %= len(script)
            y %= len(script[0])
            if script[x][y] in ['>', '<', '^', 'v']:
                dir = script[x][y]
            scr = script[x][y]
            if string_mode and scr != '"':
                stack.append(ord(scr))
            elif scr.isdigit():
                stack.append(int(scr))
            else:
                match scr:
                    case '+':
                        stack.append(stack.pop() + stack.pop())
                    case '-':
                        stack.append(-stack.pop() + stack.pop())
                    case '*':
                        stack.append(stack.pop() * stack.pop())
                    case '/':
                        a = stack.pop()
                        b = stack.pop()
                        stack.append(b // a)
                    case '%':
                        a = stack.pop()
                        b = stack.pop()
                        stack.append(b % a)
                    case '!':
                        if stack.pop():
                            stack.append(0)
                        else:
                            stack.append(1)
                    case '`':
                        a = stack.pop()
                        b = stack.pop()
                        if b > a:
                            stack.append(1)
                        else:
                            stack.append(0)
                    case '?':
                        dir = ['>', '<', 'v', '^'][random.randint(0, 3)]
                    case '_':
                        if stack.pop():
                            dir = '<'
                        else:
                            dir = '>'
                    case '|':
                        if stack.pop():
                            dir = '^'
                        else:
                            dir = 'v'
                    case '"':
                        string_mode = not string_mode
                    case ':':
                        stack.extend(2*[stack.pop()])
                    case '\\':
                        a = stack.pop()
                        b = stack.pop()
                        stack.append(a)
                        stack.append(b)
                    case '$':
                        stack.pop()
                    case '.':
                        print(stack.pop(), end='')
                    case ',':
                        print(chr(stack.pop()), end='')
                    case '#':
                        x, y = move(x, y, dir)
                        x %= len(script)
                        y %= len(script[0])
                    case 'g':
                        yg = stack.pop()
                        xg = stack.pop()
                        try:
                            stack.append(ord(script[xg][yg]))
                        except IndexError:
                            stack.append(0)
                    case 'p':
                        yp = stack.pop()
                        xp = stack.pop()
                        v = stack.pop()
                        try:
                            script[xp][yp] = chr(v)
                        except IndexError:
                            while len(script) <= xp:
                                script.append([])
                            column = script[xp]
                            if len(column) <= yp:
                                padding_needed = (yp + 1) - len(column)
                                column.extend([' '] * padding_needed)
                            script[xp][yp] = chr(v)
                    case '&':
                        ch = '\n'
                        while ch == '\n':
                            ch = sys.stdin.read(1)
                        if ch == "":
                            stack.append(0)
                        else:
                            stack.append(int(ch))
                    case '~':
                        ch = '\n'
                        while ch == '\n':
                            ch = sys.stdin.read(1)
                        if ch == "":
                            stack.append(0)
                        else:
                            stack.append(ord(ch))
            x, y = move(x, y, dir)
            x %= len(script)
            y %= len(script[0])
    except Exception as e:
        if not debug:
            print(f'File "{file}", line {y + 1}, column {x + 2}')
            print(f', character {script[x][y]} error {type(e).__name__}')
        else:
            raise e

if __name__ == '__main__':
    main()