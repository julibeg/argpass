import argparse
from enum import Enum
from typing import Any, Optional, Sequence
import sys


class NargsOption(Enum):
    COLLECT_UNTIL_NEXT_KNOWN = ""


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.special_args: dict[str, tuple[str, str]] = {}
        self.dummy_prefix_char: str = "?" if self.prefix_chars != "?" else "-"

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
                dest = (
                    arg.lstrip("-").replace("-", "_")
                    if "dest" not in kwargs
                    else kwargs["dest"]
                )
                self.special_args[arg] = ("--dummy" + arg, dest)
            kwargs["nargs"] = argparse.ZERO_OR_MORE
        return super().add_argument(*name_or_flags, **kwargs)

    def parse_known_args(  # type: ignore
        self,
        args: Optional[Sequence[str]] = None,
        namespace: Any = None,
    ) -> tuple[argparse.Namespace, list[str]]:
        args = sys.argv[1:] if args is None else list(args)
        manipulated_args: list[str] = []
        for arg in args:
            manipulated_args.append(arg)
            if arg in self.special_args:
                manipulated_args.append(self.special_args[arg][0])
        parsed_args, unknown = super().parse_known_args(manipulated_args, namespace)
        active_special_arg_dest = None
        still_unknown = []
        dummy_args = {
            dummy_arg: (arg, dest)
            for arg, (dummy_arg, dest) in self.special_args.items()
        }
        for arg in unknown:
            if arg in dummy_args:
                active_special_arg_dest = dummy_args[arg][1]
                special_arg_list = vars(parsed_args)[active_special_arg_dest]
            else:
                if active_special_arg_dest is None:
                    # unknown argument occurring before the first special argument
                    # --> remains unknown
                    still_unknown.append(arg)
                    continue
                special_arg_list.append(arg)
        unknown = [arg for arg in unknown if not arg.startswith("--dummy")]
        return parsed_args, still_unknown
