import subprocess
import sys
import tempfile
from typing import Any, Dict, NamedTuple, Type, TypeVar, List, Optional

__all__ = [
    "run_command",
    "register_ipython_excepthook",
    "to_dict",
    "to_namedtuple",
]


def run_command(args: List[str], env: Optional[Dict[bytes, bytes]] = None, cwd: Optional[str] = None,
                timeout: Optional[int] = None, **kwargs):
    r"""A wrapper over ``subprocess.check_output`` that prevents deadlock caused by the combination of pipes and
    timeout. Output is redirected into a temporary file and returned only on exceptions.
    """
    with tempfile.TemporaryFile() as f:
        try:
            subprocess.run(args, check=True, stdout=f, stderr=subprocess.STDOUT,
                           timeout=timeout, env=env, cwd=cwd, **kwargs)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            f.seek(0)
            e.output = f.read()
            raise e from None


def register_ipython_excepthook() -> None:
    r"""Register an exception hook that launches an interactive IPython session upon uncaught exceptions.
    """

    def excepthook(type, value, traceback):
        if type is KeyboardInterrupt:
            # don't capture keyboard interrupts (Ctrl+C)
            sys.__excepthook__(type, value, traceback)
        else:
            ipython_hook(type, value, traceback)

    # enter IPython debugger on exception
    from IPython.core import ultratb

    ipython_hook = ultratb.FormattedTB(mode='Context', color_scheme='Linux', call_pdb=1)
    sys.excepthook = excepthook


def to_dict(nm_tpl: NamedTuple) -> Dict[str, Any]:
    return {key: value for key, value in zip(nm_tpl._fields, nm_tpl)}


NamedTupleType = TypeVar('NamedTupleType', bound=NamedTuple)


def to_namedtuple(nm_tpl_type: Type[NamedTupleType], dic: Dict[str, Any]) -> NamedTupleType:
    return nm_tpl_type(**dic)
