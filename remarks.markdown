# My language
## How to run

```
$ sudo apt install python3
$ python3 zfc.py program.zfc
```

## Examples

* hello.zfc: Prints "Hello, World".
* truth_machine.zfc: Recieves an input, if it's 0 print 0 and exit, otherwise print 1 forever.
* Turing_complete.zfc: Provides example of the concepts in the proof of Turing Completeness (below).
* sets.zfc: Shows some manipulations of sets.
* vectors.zfc: Shows some manipulations of vectors.
* main.zfc: A big mess of almost all the features.

## Design
> The name is ZFC (Zermelo–Fraenkel and Choise Axiom)
> 
> * All operators and objects are mathematical objects
> * Thw concept is that every program can be written as a mathematical statement (proof of Turing-Completeness below)
> * I was sitting in a lecture of discrete math when I came up with the idea
> * It achieves its obfuscation by the fact that you need to know at least a little Set Theory to understand it, and most people dont know any Set Theory at all
> 

## Implementation
> 
> * Was implemented using python
> * It uses the ZFCSet class (in ZFCSet.py) to simulate sets
> * The program is being tokenized recursively then evaluated recursively
> * Every statement has a value
> * Each evaluation call run a block (or single line) of code, and returns the value of the last statement

> * There are no floating point numbers. all numbers are either integers or Rationals, using Rational class (from Rational.py)
> 

## Limitation


* The language doesn't handle exatcly correct infinite sets.
* What it can do with them correctly:
> * Given the rule of the set (for exmple odd numbers {n in Z|n%2=1}) the program can determine if given object is in it
> * It can Intersect and Union them with other (possibly infinite) sets
* It cannot:
> * Check if something is a subset
> * Find correct cardinality (all sets are assumed to have Aleph_0 cardinality unless created using Power set function)
> * Check if sets are equal

## Turing-Completeness
The language can express all brainfuck program and therefore Turing complete, because brainfuck is turing complete.

Proof of said statement:
You can initialize a Vector with length, say, 256 of zeros using the function nullVector(256), and create an integer pointer i=0 and length tracker n=256.
Loops can be used with Sigma the other Operators (Cup, Cap, Pi), and the others feature of brainfuck are pretty trivial.
When i>=n we can extend the vector by creating a temporary longer one and coping the values to the new one (shown in Turing_complete.zfc)