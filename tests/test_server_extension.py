"""Tests for the nb-nebi-kernels Jupyter Server extension."""

from types import SimpleNamespace
from typing import Any

from nb_nebi_kernels import (
    _jupyter_server_extension_points,
    _load_jupyter_server_extension,
)
from nb_nebi_kernels.server_extension import (
    KernelDiscoveryRefreshHandler,
    invalidate_kernel_discovery_cache,
    setup_handlers,
)


class _FakeWebApp:
    def __init__(self) -> None:
        self.settings = {"base_url": "/user/test/"}
        self.registered_handlers: list[tuple[str, list[tuple[str, Any, dict[str, Any]]]]] = []

    def add_handlers(
        self, host_pattern: str, handlers: list[tuple[str, Any, dict[str, Any]]]
    ) -> None:
        self.registered_handlers.append((host_pattern, handlers))


class _FakeKernelSpecManager:
    def __init__(self) -> None:
        self.invalidated = False

    def invalidate_discovery_cache(self) -> None:
        self.invalidated = True


def test_setup_handlers_registers_refresh_endpoint() -> None:
    """The extension registers the owned Nebi kernel refresh endpoint."""
    web_app = _FakeWebApp()
    server_app = SimpleNamespace(kernel_spec_manager=_FakeKernelSpecManager())

    setup_handlers(web_app, server_app)

    assert web_app.registered_handlers == [
        (
            ".*$",
            [
                (
                    "/user/test/nb-nebi-kernels/kernels/refresh",
                    KernelDiscoveryRefreshHandler,
                    {"server_app": server_app},
                )
            ],
        )
    ]


def test_invalidate_kernel_discovery_cache_calls_manager() -> None:
    """Cache invalidation is delegated to the active kernelspec manager."""
    manager = _FakeKernelSpecManager()
    server_app = SimpleNamespace(kernel_spec_manager=manager)

    assert invalidate_kernel_discovery_cache(server_app) is True
    assert manager.invalidated is True


def test_invalidate_kernel_discovery_cache_reports_unsupported_manager() -> None:
    """The endpoint can report when the active manager has no Nebi cache."""
    server_app = SimpleNamespace(kernel_spec_manager=object())

    assert invalidate_kernel_discovery_cache(server_app) is False


def test_jupyter_server_extension_entrypoint_loads_handlers() -> None:
    """The top-level package is loadable as a Jupyter Server extension."""
    web_app = _FakeWebApp()
    server_app = SimpleNamespace(
        web_app=web_app,
        kernel_spec_manager=_FakeKernelSpecManager(),
    )

    assert _jupyter_server_extension_points() == [
        {"module": "nb_nebi_kernels", "name": "nb_nebi_kernels"}
    ]

    _load_jupyter_server_extension(server_app)

    assert web_app.registered_handlers
