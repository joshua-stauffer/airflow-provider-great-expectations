from great_expectations_provider.operators.constants import VERSION

__version__ = VERSION


def get_provider_info():
    return {
        "package-name": "airflow-provider-great-expectations",
        "name": "Great Expectations Provider",
        "description": "An Apache Airflow provider for Great Expectations.",
        "versions": [__version__],
        "hooks": [
            {
                "integration-name": "GX Cloud",
                "python-modules": ["great_expectations_provider.hooks.gx_cloud"],
            }
        ],
        "connection-types": [
            {
                "connection-type": "gx_cloud",
                "hook-class-name": "great_expectations_provider.hooks.gx_cloud.GXCloudHook",
                "hook-name": "Great Expectations Cloud",
            }
        ],
    }
