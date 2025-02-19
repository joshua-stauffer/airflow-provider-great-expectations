from __future__ import annotations

from functools import cached_property
from typing import Any

from airflow.hooks.base import BaseHook


class GXCloudConnection(BaseHook):
    """
    Connect to the GX Cloud managed backend.

    :param organization_id: Organization ID of the GX cloud account.
    :param token: GX cloud access token.
    """

    conn_name_attr = "gx_cloud_config_id"
    default_conn_name = "gx_cloud_default"
    conn_type = "gx_cloud"
    hook_name = "GX Cloud Connection"

    def __init__(self, gx_cloud_config_id: str = default_conn_name):
        super().__init__()
        self.gx_cloud_config_id = gx_cloud_config_id

    @cached_property
    def get_conn(self) -> dict[str, str]:  # type: ignore[override]
        config = self.get_connection(self.gx_cloud_config_id)
        return {
            "cloud_access_token": config.password,
            "cloud_organization_id": config.login,
        }

    @classmethod
    def get_ui_field_behaviour(cls) -> dict[str, Any]:
        """Return custom field behaviour."""
        return {
            "hidden_fields": ["schema", "port", "extra"],
            "relabeling": {
                "login": "Organization ID",
                "password": "API Key",
            },
            "placeholders": {},
        }

    def test_connection(self) -> tuple[bool, str]:
        try:
            config = self.get_connection(self.gx_cloud_config_id)
            import great_expectations as gx

            gx.get_context(
                mode="cloud",
                cloud_access_token=config.password,
                cloud_organization_id=config.login,
            )
            return True, "Connection successful."
        except Exception as error:
            return False, str(error)
