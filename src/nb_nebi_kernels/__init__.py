from typing import Any

from nb_nebi_kernels._version import __version__
from nb_nebi_kernels.manager import NebiKernelSpecManager

__all__ = ["NebiKernelSpecManager", "__version__"]


def _jupyter_server_extension_points() -> list[dict[str, str]]:
    return [{"module": "nb_nebi_kernels", "name": "nb_nebi_kernels"}]


def _load_jupyter_server_extension(server_app: Any) -> None:
    from nb_nebi_kernels.server_extension import load_jupyter_server_extension

    load_jupyter_server_extension(server_app)
