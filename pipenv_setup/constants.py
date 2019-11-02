from enum import Enum
from typing import Union, Dict, Any

PipfileConfig = Union[dict, str]
LockConfig = Dict[str, Any]

vcs_list = ["git", "bzr", "svn", "hg"]


class VersionConflict(Enum):
    # >=2.0 potentially violates >=3.0
    POTENTIAL = "POTENTIAL"

    # <=2.0 is disjoint with >=3.0
    DISJOINT = "DISJOINT"

    # >=3.0 is compatible with >=2.0
    COMPATIBLE = "COMPATIBLE"
