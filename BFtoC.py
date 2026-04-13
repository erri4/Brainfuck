import os
import argparse
import re
from itertools import groupby

# nuitka --onefile --standalone --follow-imports --windows-console-mode=force ./brainfuck.py
def parse(code: str, debug: bool = False):
    valid_commands = {'>', '<', '+', '-', '.', ',', '[', ']', ';', '#', '!'} if debug else {'>', '<', '+', '-', '.', ',', '[', ']', ';'}
    return ''.join([char for char in code if char in valid_commands])


def is_valid_window(window: list[tuple[str, int] | str]):
    if window[0] != '[' or window[5] != ']':
        return False
    
    ops = [w[0] for w in window[1:5] if isinstance(w, tuple)]
    offset = 0
    for x in window[1:5]:
        if isinstance(x, tuple):
            if x[0] == '>':
                offset += x[1]
            if x[0] == '<':
                offset -= x[1]
    
    return ops in [
        ['-', '>', '+', '<'],
        ['>', '+', '<', '-'],
        ['<', '+', '>', '-'],
        ['-', '<', '+', '>'],
        ['+', '>', '-', '<'],
        ['>', '-', '<', '+'],
        ['<', '-', '>', '+'],
        ['+', '<', '-', '>'],
    ] and offset == 0


def compress_window(window: list[tuple[str, int]]):
    return window[1:5]


def replace_patterns(lst: list[tuple[str, int] | str]):
    i = 0
    result = []
    
    while i < len(lst):
        window = lst[i:i+6]
        
        if len(window) == 6 and is_valid_window(window):
            result.append(compress_window(window))
            i += 6
        else:
            result.append(lst[i])
            i += 1
    
    return result


def is_match(window: list[tuple[str, int] | str]):
    ops = [(w[0] if isinstance(w, tuple) else w) for w in window]
    offset = 0
    for x in window:
        if isinstance(x, tuple):
            if x[0] == '>':
                offset += x[1]
            if x[0] == '<':
                offset -= x[1]
    
    return ops in [
        ['>', '+', '<'],
        ['<', '+', '>'],
        ['>', '-', '<'],
        ['<', '-', '>'],
        ['<', ',', '>'],
        ['>', ',', '<'],
        ['<', '.', '>'],
        ['>', '.', '<'],
        ['<', 'c', '>'],
        ['>', 'c', '<'],
        ['>', ';', '<'],
        ['<', ';', '>'],
    ] and offset == 0


def replace_pattern2(lst: list[tuple[str, int] | str]):
    i = 0
    result = []
    
    while i < len(lst):
        window = lst[i:i+3]
        
        if len(window) == 3 and is_match(window):
            result.append(('off', window[0][1] if window[0][0] == '>' else -window[0][1], (window[1][0] if isinstance(window[1], tuple) else window[1], window[1][1] if isinstance(window[1], tuple) else 1)))
            i += 3
        else:
            result.append(lst[i])
            i += 1
    
    return result


def optimize(script: str):
    script = list(script)
    i = 0
    while i < len(script) - 1:
        if script[i] == ']' and script[i + 1] == '[':
            j = i + 1
            depth = 1
            while depth > 0 and j < len(script):
                j += 1
                if script[j] == '[':
                    depth += 1
                if script[j] == ']':
                    depth -= 1
            if depth == 0 and j < len(script):
                del script[i+1:j + 1]
        else:
            i += 1
    script = ''.join(script)
    replacements = {
        '[-]': 'c',
        '[+]': 'c',
        '[<]': 'l',
        '[>]': 'r',
        '<>': '',
        '><': '',
        '+-': '',
        '-+': '',
        }
    while '<>' in script or '><' in script or '+-' in script or '-+' in script:
        pattern = re.compile("|".join(re.escape(k) for k in replacements))
        script = pattern.sub(lambda m: replacements[m.group(0)], script)
    pattern = re.compile("|".join(re.escape(k) for k in replacements))
    script = pattern.sub(lambda m: replacements[m.group(0)], script)
    script = list(script)

    compressed = []
    
    for char, group in groupby(script):
        group_list = list(group)
        count = len(group_list)
        
        if char in "><+-" and count > 1:
            compressed.append((char, count))
        else:
            for _ in range(count):
                compressed.append((char, 1) if char not in {',', '.', '[', ']', 'c', ';', '#', '!', 'l', 'r'} else char)
    compressed = replace_patterns(compressed)
    compressed = replace_pattern2(compressed)
    return compressed


def main():
    parser = argparse.ArgumentParser(description="Brainfuck interpreter/compiler.")
    parser.add_argument("script", help="Path to the Brainfuck script to run")

    parser.add_argument("--debug", action="store_true", help="Debug")

    args = parser.parse_args()

    with open(args.script) as f:
        script = optimize(parse(f.read(), args.debug))
    compile(script, args.debug, args.script)
    

def compile(script: list[str], debug: bool = False, file: str = ''):
    def compile_to_c(tokens: list[str]):
        c_program = []
        indent_level = 1  
        
        def indent(i: int = 0):
            return "    " * (indent_level + i)
        
    
        c_program.append("#include <stdio.h>")
        if 'r' in tokens:
            c_program.append("#include <string.h>")
        if 'l' in tokens:
            c_program.append('''#include <stddef.h>
void *memrchr(const void *ptr, int value, size_t num) {
    const unsigned char *p = (const unsigned char *)ptr + num;

    while (p != (const unsigned char *)ptr) {
        p--;
        if (*p == (unsigned char)value)
            return (void *)p;
    }
    return NULL;
}''')
            if 4 in [len(x) for x in tokens]:
                c_program.append('''typedef unsigned char u8;
int gcd(int a, int b) {
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int modinv(int a, int m) {
    int t = 0, newt = 1;
    int r = m, newr = a;

    while (newr != 0) {
        int q = r / newr;

        int tmp = newt;
        newt = t - q * newt;
        t = tmp;

        tmp = newr;
        newr = r - q * newr;
        r = tmp;
    }

    if (r > 1) return -1;
    if (t < 0) t += m;

    return t;
}

int find_k(unsigned char n, unsigned char m) {
    if (m == 0) return -1;

    int d = gcd(256, m);

    if (n % d != 0) return -1;

    int n_ = n / d;
    int m_ = m / d;
    int a_ = 256 / d;

    int inv = modinv(a_ % m_, m_);
    if (inv == -1) return -1;

    int k = (-n_ * inv) % m_;
    if (k < 0) k += m_;

    return k;
}
                                 
int k;''')
        c_program.append("int main() {")
        c_program.append("    unsigned char mem[65536] = {0};")
        c_program.append("    int used = 0;")
        c_program.append("    unsigned char *pointer = mem;")
    
    
        for token in tokens:
            if token == '>':
                c_program.append(indent() + f"pointer++;")
                c_program.append(indent() + "if (pointer - mem > used) used++;")
            elif token == '<':
                c_program.append(indent() + f"pointer--;")
            elif token == '+':
                c_program.append(indent() + f"(*pointer)++;")
            elif token == '-':
                c_program.append(indent() + f"(*pointer)--;")
            elif token == '.':
                c_program.append(indent() +f"putchar(*pointer);")
            elif token == ';':
                c_program.append(indent() + f'printf("%d", *pointer);')
            elif token == ',':
                c_program.append(indent() + f"(*pointer) = getchar();")
            elif token == '[':
                c_program.append(indent() + "while (*pointer) {")
                indent_level += 1
            elif token == ']':
                indent_level -= 1
                c_program.append(indent() + "}")
            elif token == 'c':
                c_program.append(indent() + '(*pointer) = 0;')
            elif token == 'r':
                c_program.append(indent() + "pointer = memchr(pointer, 0, mem + 65536 - pointer);")
            elif token == 'l':
                c_program.append(indent() + "pointer = memrchr(mem, 0, pointer - mem);")
            elif len(token) == 2:
                if token[0] == '+':
                    c_program.append(indent() + f'(*pointer) += {token[1]};')
                if token[0] == '-':
                    c_program.append(indent() + f'(*pointer) -= {token[1]};')
                if token[0] == '>':
                    c_program.append(indent() + f'pointer += {token[1]};')
                    c_program.append(indent() + "if (pointer - mem > used) used = pointer - mem;")
                if token[0] == '<':
                    c_program.append(indent() + f'pointer -= {token[1]};')
            elif len(token) == 3:
                if token[0] == 'off':
                    c_program.append(indent() + f"if (pointer + {token[1]} - mem > used) used = pointer - mem;")
                    match token[2][0]:
                        case '+':
                            c_program.append(indent() + f'*(pointer + {token[1]}) += {token[2][1]};')
                        case '-':
                            c_program.append(indent() + f'*(pointer + {token[1]}) -= {token[2][1]};')
                        case ',':
                            c_program.append(indent() + f'*(pointer + {token[1]}) = getchar();')
                        case '.':
                            c_program.append(indent() + f'putchar(*(pointer + {token[1]}));')
                        case 'c':
                            c_program.append(indent() + f'*(pointer + {token[1]}) = 0;')
                        case ';':
                            c_program.append(indent() + f'printf("%d", *(pointer + {token[1]}));')
            if len(token) == 4:
                match [x[0] for x in token if isinstance(x, tuple)]:
                    case ['-', '>', '+', '<']:
                        c_program.append(indent() + f'k = find_k(*pointer, {token[0][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + 'while (*pointer){')
                        c_program.append(indent(2) + f'*(pointer) -= {token[0][1]};')
                        c_program.append(indent(2) + f'*(pointer + {token[1][1]}) += {token[2][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + 'int tmp = (*pointer) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer + {token[1][1]}) += tmp * {token[2][1]} / {token[0][1]};')
                        c_program.append(indent(1) + '*(pointer) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
                    case ['>', '+', '<', '-']:
                        c_program.append(indent() + f'k = find_k(*pointer, {token[3][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + 'while (*pointer){')
                        c_program.append(indent(2) + f'*(pointer) -= {token[3][1]};')
                        c_program.append(indent(2) + f'*(pointer + {token[0][1]}) += {token[1][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + 'int tmp = (*pointer) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer + {token[0][1]}) += tmp * {token[1][1]} / {token[3][1]};')
                        c_program.append(indent(1) + '*(pointer) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
                    case ['<', '+', '>', '-']:
                        c_program.append(indent() + f'k = find_k(*pointer, {token[3][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + 'while (*pointer){')
                        c_program.append(indent(2) + f'*(pointer) -= {token[3][1]};')
                        c_program.append(indent(2) + f'*(pointer - {token[0][1]}) += {token[1][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + 'int tmp = (*pointer) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer - {token[0][1]}) += tmp * {token[1][1]} / {token[3][1]};')
                        c_program.append(indent(1) + '*(pointer) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
                    case ['-', '<', '+', '>']:
                        c_program.append(indent() + f'k = find_k(*pointer, {token[0][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + 'while (*pointer){')
                        c_program.append(indent(2) + f'*(pointer) -= {token[0][1]};')
                        c_program.append(indent(2) + f'*(pointer - {token[1][1]}) += {token[1][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + 'int tmp = (*pointer) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer - {token[1][1]}) += tmp * {token[2][1]} / {token[0][1]};')
                        c_program.append(indent(1) + '*(pointer) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
                    case ['+', '>', '-', '<']:
                        c_program.append(indent() + f'k = find_k(*(pointer + {token[1][1]}), {token[2][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + f'while (*(pointer + {token[1][1]}))' + '{')
                        c_program.append(indent(2) + f'*(pointer + {token[1][1]}) -= {token[2][1]};')
                        c_program.append(indent(2) + f'*(pointer) += {token[0][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + f'int tmp = (*(pointer + {token[1][1]})) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer) += tmp * {token[0][1]} / {token[2][1]};')
                        c_program.append(indent(1) + f'*(pointer + {token[1][1]}) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
                    case ['>', '-', '<', '+']:
                        c_program.append(indent() + f'k = find_k(*(pointer + {token[0][1]}), {token[1][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + f'while (*(pointer + {token[0][1]}))' + '{')
                        c_program.append(indent(2) + f'*(pointer + {token[0][1]}) -= {token[1][1]};')
                        c_program.append(indent(2) + f'*(pointer) += {token[3][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + f'int tmp = (*(pointer + {token[0][1]})) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer) += tmp * {token[3][1]} / {token[1][1]};')
                        c_program.append(indent(1) + f'*(pointer + {token[0][1]}) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
                    case ['<', '-', '>', '+']:
                        c_program.append(indent() + f'k = find_k(*(pointer - {token[0][1]}), {token[1][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + f'while (*(pointer - {token[0][1]}))' + '{')
                        c_program.append(indent(2) + f'*(pointer - {token[0][1]}) -= {token[1][1]};')
                        c_program.append(indent(2) + f'*(pointer) += {token[3][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + f'int tmp = (*(pointer - {token[0][1]})) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer) += tmp * {token[3][1]} / {token[1][1]};')
                        c_program.append(indent(1) + f'*(pointer - {token[0][1]}) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
                    case ['+', '<', '-', '>']:
                        c_program.append(indent() + f'k = find_k(*(pointer - {token[1][1]}), {token[2][1]});')
                        c_program.append(indent() + 'if (k == -1){')
                        c_program.append(indent(1) + f'while (*(pointer - {token[1][1]}))' + '{')
                        c_program.append(indent(2) + f'*(pointer - {token[1][1]}) -= {token[2][1]};')
                        c_program.append(indent(2) + f'*(pointer) += {token[0][1]};')
                        c_program.append(indent(1) + '}')
                        c_program.append(indent() + '}')
                        c_program.append(indent() + 'else {')
                        c_program.append(indent(1) + f'int tmp = (*(pointer - {token[1][1]})) + 256 * k;')
                        c_program.append(indent(1) + f'*(pointer) += tmp * {token[0][1]} / {token[2][1]};')
                        c_program.append(indent(1) + f'*(pointer - {token[1][1]}) = 0;')
                        c_program.append(indent(1) + 'tmp = 0;')
                        c_program.append(indent() + '}')
            elif token == '#' and debug:
                c_program.append(indent() + "printf(\"[\");")
                c_program.append(indent() + "for(int i = 0; i < used; i++) {")
                c_program.append(indent() + "    printf(\"%u, \", mem[i]);")
                c_program.append(indent() + "}")
                c_program.append(indent() + "printf(\"%u]\", mem[used]);")
            elif token == '!' and debug:
                c_program.append(indent() + "printf(\"%u\", pointer - mem);")
        
    
        c_program.append("    return 0;")
        c_program.append("}")
        
        return "\n".join(c_program)
    
    c_output = compile_to_c(script)
    with open(os.path.basename(os.path.splitext(file)[0]) + '.c',"w") as f:
        f.write(c_output)


if __name__ == '__main__':
    main()