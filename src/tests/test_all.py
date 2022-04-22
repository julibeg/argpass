import argpass
import pytest

args = """--file test.txt --regular-arg testArg
    --args-to-pass-on-1 --param1 val1 --param2 val2
    --args-to-pass-on-2 bla --param3 val3 --blu""".split()
args_with_unknown = """--file test.txt --regular-arg testArg
    --unknown1 unknown2 --unknown3
    --args-to-pass-on-1 --param1 val1 --param2 val2
    --args-to-pass-on-2 bla --param3 val3 --blu""".split()
parsed_expected = dict(
    file="test.txt",
    regular_arg="testArg",
    args_to_pass_on_1=["--param1", "val1", "--param2", "val2"],
    args_to_pass_on_2=["bla", "--param3", "val3", "--blu"],
)
unknown_expected = ["--unknown1", "unknown2", "--unknown3"]

parser = argpass.ArgumentParser(prefix_chars='?-+_#')
parser.add_argument("--file")
parser.add_argument("--regular-arg")
parser.add_argument(
    "--args-to-pass-on-1", nargs=argpass.NargsOption.COLLECT_UNTIL_NEXT_KNOWN
)
parser.add_argument(
    "--args-to-pass-on-2", nargs=argpass.NargsOption.COLLECT_UNTIL_NEXT_KNOWN
)


def test_parse_args_without_unknown_args():
    parsed = parser.parse_args(args)
    assert vars(parsed) == parsed_expected
    parsed, unknown = parser.parse_known_args(args)
    assert vars(parsed) == parsed_expected
    assert unknown == []


def test_parse_args_with_unknown_args():
    with pytest.raises(SystemExit) as e:
        parser.parse_args(args_with_unknown)
    assert e.value.code == 2


def test_parse_known_args_with_unknown_args():
    parsed, unknown = parser.parse_known_args(args_with_unknown)
    assert vars(parsed) == parsed_expected
    assert unknown == unknown_expected
