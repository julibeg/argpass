import argparse
from enum import Enum
from typing import Any, Optional, Sequence, Dict, Tuple, List
import sys

SPECIAL_CHARACTERS = list("?!#$%&()*+,-./:;<=>@[]^_{|}")


class NargsOption(Enum):
    COLLECT_UNTIL_NEXT_KNOWN = ""


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.dummy_args: Dict[str, str] = {}
        self.dummy_prefix_char: str
        for char in SPECIAL_CHARACTERS:
            if char not in self.prefix_chars:
                self.dummy_prefix_char = char
                break
        else:
            raise ValueError(
                "Could not find suitable prefix character for dummy arguments"
            )

    def add_argument(
        self,
        *name_or_flags: Any,
        **kwargs: Any,
    ) -> argparse.Action:
        if (
            "nargs" in kwargs
            and kwargs["nargs"] == NargsOption.COLLECT_UNTIL_NEXT_KNOWN
        ):
            for arg in name_or_flags:
                dummy_arg = f"{self.dummy_prefix_char}dummy{arg}"
                self.dummy_args[arg] = dummy_arg
            kwargs["nargs"] = 1
        return super().add_argument(*name_or_flags, **kwargs)

    def parse_known_args(
        self,
        args: Optional[Sequence[str]] = None,
        namespace: Any = None,
    ) -> Tuple[argparse.Namespace, List[str]]:
        args = sys.argv[1:] if args is None else list(args)
        manipulated_args: List[str] = []
        for arg in args:
            manipulated_args.append(arg)
            if arg in self.dummy_args:
                manipulated_args.append(self.dummy_args[arg])
                manipulated_args.append(self.dummy_args[arg])
        parsed_args, unknown = super().parse_known_args(manipulated_args, namespace)
        # parse again using the dummy prefix
        dummy_parser = argparse.ArgumentParser(prefix_chars=self.dummy_prefix_char)
        for arg, dummy_arg in self.dummy_args.items():
            dummy_parser.add_argument(dummy_arg, dest=dummy_arg, nargs="+")
        parsed_dummy_args, still_unknown = dummy_parser.parse_known_args(unknown)
        # replace the dummy args in the originally parsed arguments
        for dest, arg in vars(parsed_args).items():
            if (
                isinstance(arg, list)
                and len(arg) == 1
                and arg[0] in self.dummy_args.values()
            ):
                vars(parsed_args)[dest] = vars(parsed_dummy_args)[arg[0]]
        return parsed_args, still_unknown
