[
    move from cell x to cell n:
        x[-n+x]
    copy from cell x to cell n (m is an open cell):
        x[-n+m+x]m[-x+m]x
    y=1 if x=0 else y=0 (empties x):
        x[y-x[-]]y+x
    adds x+y and puts in x (m is an open cell):
        y[-x+m+y]m[-y+m]x
    y=1 if x=0 else y=0 (does not empty x) (m is an open cell):
        x[-m+y+x]y[-x+y]x[y-x[-]]y+m[-x+m]x
    empty cell x:
        x[-]
    div by 2 (m empty cell):
        x[--m+x]m[-x+m]x
    48 (y empty cell):
        xy++++++[-x++++++++y]x
    distribute n+1 ones on the n+1 cells after x where (n) notates *set this cell to value n* (x must be 0):
        x>(n)[[>]+[<]>-]+<
    compute n!mod256 where (n) notates *set this cell to value n* (uses 4 cells including x):
        x[-]+>(n)[<[->[->+>+<<]>>[-<<+>>]<<<]>->[-<<+>>]<]<
    prints liouville's constant 120 digits and return to starting index! (requires next 120 cells to be empty):
        >+>+++++[<[->[->+>+<<]>>[-<<+>>]<<<]>->[-<<+>>]<]<[[->+<]>-<+>]<+<[<]
>[-]+>[-]++++>[-]>[-]>[-]<<<[<[->[->+>+<<]>>[-<<+>>]<<<]>->[-<<+>>]<]<[>[-]<[->+<]>-<+>]+<+<[<]
>[-]+>[-]+++>[-]>[-]>[-]<<<[<[->[->+>+<<]>>[-<<+>>]<<<]>->[-<<+>>]<]<[>[-]<[->+<]>-<+>]<+<[<]
>[-]+>[-]++>[-]>[-]>[-]<<<[<[->[->+>+<<]>>[-<<+>>]<<<]>->[-<<+>>]<]<[>[-]<[->+<]>-<+>]<+<[<]
>+>>+>+>+>>+[<]>++++[-<++++++++>]<.[-]>++<++++[>+++++++++++<-]>[-<+>]<.[-]>+<++++++[->++++++++<]>.[-]>[-<++++++[->++++++++<]>.[-]>]>+>+++++[<[->[->+>+<<]>>[-<<+>>]<<<]>->[-<<+>>]<]<[[-<+>]<-]<<[>]
]