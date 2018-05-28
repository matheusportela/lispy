# lispy
Didactic Lisp interpreter in Python

## Usage

**REPL mode:**
```
$ python lispy.py
lispy v0.0.1

>>> (quote 1 2 3)
(1 2 3)
>>> (+ 1 2 3)
6
>>> (+ 1 2 (+ 3 4) 5)
15
```

**Interpreter mode:**
```
$ python lispy.py hello_world.lisp
Hello, world!
```

## Test

```shell
$ python test_lispy.py
```

## Standard Library
`quote`: Avoid evaluation of the given argument
```lisp
>>> (quote foo)
foo
>>> (quote (1 2 foo))
(1 2 foo)
```

`defun`: Define functions in global scope
```lisp
>>> (defun area (r)
      (* 3.14 (pow r 2)))
:area
>>> (area 10)
314.0
```

`if`: Conditional expression
```lisp
>>> (set password "123456")
nil
>>> (if (= (get password) "123456")
        (write "Logged in")
        (write "Wrong password"))
Logged in
nil
>>> (set password "654321")
nil
>>> (if (= (get password) "123456")
        (write "Logged in")
        (write "Wrong password"))
Wrong password
nil
```

`let`: Create local variables
```lisp
>>> (let ((x 1)
          (y 2))
      (+ x y))
3
```

`progn`: Execute sequential expressions
```lisp
>>> (progn
      (write "Hello")
      (write "What's your name?"))
Hello
What's your name?
nil
```

`set`: Set value to global variable
```lisp
>>> (set (quote *foo*) 42)
nil
```

`get`: Get value from previous defined global variable
```lisp
>>> (set (quote *foo*) 42)
nil
>>> (get (quote *foo*))
42
```

`list`: Create list evaluating the given arguments
```lisp
>>> (list 1)
(1)
>>> (list 1 2 (+ 3 4))
(1 2 7)
```

`=`: Verify whether two elements are equivalents
```lisp
>>> (= 1 1)
t
>>> (= 1 1.0)
t
>>> (= 1 2)
nil
>>> (= 1 "a")
nil
```

`+` or `sum`: Sum all arguments
```lisp
>>> (+ 1 2 3)
6
>>> (sum 1 2 (+ 3 4) 5)
15
```

`-` or `sub`: Subtract two arguments
```lisp
>>> (- 1 2)
-1
>>> (sub 1 (- 2 3))
2
```

`*` or `mul`: Multiply all arguments
```lisp
>>> (* 1 2 3)
6
>>> (mul 1 2 (* 3 4))
24
```

`/` or `div`: Divide two arguments
```lisp
>>> (/ 1 2)
0.5
>>> (div 1 (/ 2 3))
1.5

`pow`: Raise the first element to the power defined in the second one
```lisp
>>> (pow 10 3)
1000
>>> (pow 25 (/ 1 2))
5.0
```

`write`: Write string to the standard output
```lisp
>>> (write "Hello, world!")
Hello, world!
nil
```

`read`: Return string read from standard input
```lisp
>>> (set name (read))
Joe
nil
>>> (get name)
Joe
>>> (set age (int (read)))
25
nil
>>> (get age)
25
```


`concat`: Concatenate strings
```lisp
>>> (concat "Hello" ", " "world" "!")
Hello, world!
```

`float`: Cast value to float number
```lisp
>>> (float 10)
10.0
```

`int`: Cast value to integer number
```lisp
>>> (int 10.0)
10
>>> (int 10.5)
10
```

`str`: Cast value to string
```lisp
>>> (str 10)
10
>>> (str 10.5)
10.5
```
