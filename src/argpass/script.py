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
