from great_expectations_provider.operators.validate_batch import GXValidateBatchOperator
from great_expectations_provider.operators.validate_dataframe import GXValidateDataFrameOperator
from great_expectations_provider.operators.validate_checkpoint import GXValidateCheckpointOperator

__version__ = "1.0.0"


def get_provider_info():
    return {
        "package-name": "airflow-provider-great-expectations",
        "name": "Great Expectations Provider",
        "description": "An Apache Airflow provider for Great Expectations.",
        "versions": [__version__],
    }
