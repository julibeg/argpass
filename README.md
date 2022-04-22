![Python tests](https://github.com/julibeg/argpass/workflows/Tests/badge.svg)
# argpass
An argparse extension to collect and pass on command line arguments (potentially starting with hyphens) to other programs.

## TL;DR:
Imagine writing a wrapper script that calls two or more other programs. In many cases, you will want to collect command line arguments for these programs and pass them on unaltered. Using [argparse](https://docs.python.org/3/library/argparse.html), this is not possible. With `argpass`, simply pass `nargs=argpass.NargsOption.COLLECT_UNTIL_NEXT_KNOWN` to `parser.add_argument` and it will collect all strings (regardless of format) until the next known argument.

## Installation
Install with
```
pip install argpass
```

## Motivation
Built-in [argparse](https://docs.python.org/3/library/argparse.html) lacks an option to ignore unrecognized flag strings (usually starting with `-` or `--`), which makes it difficult to collect arguments and pass them on to other programs in some cases. It can be done with `ArgumentParser.parse_known_args` (see [docs](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_known_args)) which collects all unrecognized arguments, but this only works when just one other program is invoked from our script. Collecting arguments starting with dashes to pass on to more than one program is impossible with argparse, which as caused quite some [frustration](https://github.com/python/cpython/issues/53580). 

## An example
Consider the following example: We have a Python script that takes an input file, a regular argument, and other arguments that should be passed on to another program which is invoked from within our script. We would call our script as follows:
```
python script.py --file example.txt --regular-arg exampleArg --args-to-pass-on --param1 val1 --param2 val2
```
Thanks to `ArgumentParser.parse_known_args`, this case can be handled by [argparse](https://docs.python.org/3/library/argparse.html) just fine:
```python
$ cat script.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--file")
parser.add_argument("--regular-arg")
parser.add_argument("--args-to-pass-on", nargs="*")
args, unknown = parser.parse_known_args()
args.args_to_pass_on = unknown
print(args)

$ python script.py --file example.txt --regular-arg exampleArg --args-to-pass-on --param1 val1 --param2 val2
Namespace(file='example.txt', regular_arg='exampleArg', args_to_pass_on=['--param1', 'val1', '--param2', 'val2'])
```
However, this approach only works when we want to collect arguments for just a single program. Doing something like 
```
python script.py \
    --file example.txt --regular-arg exampleArg \
    --args-to-pass-on-1 --param1 val1 --param2 val2 \
    --args-to-pass-on-2 bla --param3 val3 --blu
```
cannot be achieved with argparse. 

`argpass` is a thin wrapper around argparse that allows you to do exactly that. When adding another paramater to the parser, simply specify `nargs=NargsOption.COLLECT_UNTIL_NEXT_KNOWN` and `argpass` will collect all strings until the next known argument:
```python
$ cat script.py
import argpass

parser = argpass.ArgumentParser()
parser.add_argument("--file")
parser.add_argument("--regular-arg")
parser.add_argument(
    "--args-to-pass-on-1", nargs=argpass.NargsOption.COLLECT_UNTIL_NEXT_KNOWN
)
parser.add_argument(
    "--args-to-pass-on-2", nargs=argpass.NargsOption.COLLECT_UNTIL_NEXT_KNOWN
)
print(parser.parse_args())

$ python script.py \
    --file example.txt --regular-arg exampleArg \
    --args-to-pass-on-1 --param1 val1 --param2 val2 \
    --args-to-pass-on-2 bla --param3 val3 --blu
Namespace(file='example.txt', regular_arg='exampleArg', args_to_pass_on_1=['--param1', 'val1', '--param2', 'val2'], args_to_pass_on_2=['bla', '--param3', 'val3', '--blu'])
```
