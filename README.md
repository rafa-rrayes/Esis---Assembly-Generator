Gerador de assembly para o cpu Z01 feito em Elementos de Sistemas.

Esis.py - É o código que gera o assembly. 

nasmSim_GUI - É o código para o simulador de assembly.
dois exemplos foram inclusos para testar.

# Esis

## Introduction
This repository contains a Python script for translating a custom high-level programming language into the assembly language used by the Z01 CPU, developed in Elementos de Sistemas course. This README will guide you through understanding the structure of the translator, how to use it, and how to write code in the custom language that can be translated into assembly.

## Table of Contents
- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
- [Writing Code](#writing-code)
  - [Variables](#variables)
  - [Arithmetic Operations](#arithmetic-operations)
  - [Logical Operations](#logical-operations)
  - [Control Flow](#control-flow)
  - [Functions](#functions)
  - [Function Calls](#function-calls)
- [Examples](#examples)
  - [Factorial Calculation](#factorial-calculation)
  - [Division Calculation](#division-calculation)
## Writing Code

The custom language supports variable assignment, arithmetic operations, logical operations, control flow (if statements, while loops), and functions. Here's a guide on how to write code in this language.

### Variables

Variables are assigned using the `=` operator:
```plaintext
A = 5
B = A
```

### Arithmetic Operations

You can perform basic arithmetic operations:
- Addition: `+`
- Subtraction: `-`

```plaintext
C = A + B
D = A - 3
```

### Logical Operations

You can use logical operations for conditional checks:
- AND: `&`
- OR: `|`

```plaintext
E = A & B
F = A | B
```

### Control Flow

#### If Statements
If statements check a condition and execute a function if the condition is true:
```plaintext
if A > B: someFunction
```

Supported comparison operators:
- Equal: `==`
- Not equal: `!=`
- Greater than: `>`
- Less than: `<`
- Greater than or equal: `>=`
- Less than or equal: `<=`

#### While Loops
While loops repeatedly execute a block of code as long as the condition is true:
```plaintext
while A > 0 {
    A = A - 1
}
```

### Functions

Define functions using the `def` keyword. Functions must have a unique name and be enclosed in curly braces `{}`:
```plaintext
def myFunction {
    // Function code here
}
```

### Function Calls

Call a function using its name followed by `()`:
```plaintext
myFunction()
```

## Examples

### Factorial Calculation

```plaintext
A = 5
C = A - 1
def fact {
    while C > 1 {
        B = C
        Copia = A
        multi()
        C = C - 1
    }
}
def multi {
    while B > 1 {
        A = A + Copia
        B = B - 1
    }
}
fact()
```

### Division Calculation

```plaintext
A = 10
B = 2
resultado = 0
def sub1 {
    resultado = resultado - 1
}
def divisao {
    while A > 0 {
        A = A - B
        resultado = resultado + 1
        if A < 0: sub1
    }
}
divisao()
```
