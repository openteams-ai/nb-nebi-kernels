"""Jupyter Server extension endpoints for nb-nebi-kernels."""

from __future__ import annotations

import json
import logging
from typing import Any

import tornado.web
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

logger = logging.getLogger(__name__)

API_NAMESPACE = "nb-nebi-kernels"


def invalidate_kernel_discovery_cache(server_app: Any) -> bool:
    """Invalidate the active kernelspec manager's discovery cache when supported."""
    manager = getattr(server_app, "kernel_spec_manager", None)
    invalidate = getattr(manager, "invalidate_discovery_cache", None)
    if not callable(invalidate):
        return False

    invalidate()
    return True


class KernelDiscoveryRefreshHandler(APIHandler):
    """Invalidate Nebi kernelspec discovery before the next kernelspec request."""

    def initialize(self, server_app: Any) -> None:
        self.server_app = server_app

    @tornado.web.authenticated
    def post(self) -> None:
        invalidated = invalidate_kernel_discovery_cache(self.server_app)
        self.finish(json.dumps({"invalidated": invalidated}))


def setup_handlers(web_app: Any, server_app: Any) -> None:
    """Register nb-nebi-kernels API handlers with Jupyter Server."""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    api_url = url_path_join(base_url, API_NAMESPACE)
    handlers = [
        (
            url_path_join(api_url, "kernels", "refresh"),
            KernelDiscoveryRefreshHandler,
            {"server_app": server_app},
        )
    ]
    web_app.add_handlers(host_pattern, handlers)


def load_jupyter_server_extension(server_app: Any) -> None:
    """Load the nb-nebi-kernels Jupyter Server extension."""
    setup_handlers(server_app.web_app, server_app)
    logger.info("nb-nebi-kernels server extension loaded")
