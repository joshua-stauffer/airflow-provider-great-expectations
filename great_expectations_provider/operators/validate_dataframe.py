from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from airflow.models import BaseOperator

from great_expectations_provider.common.gx_context_actions import (
    run_validation_definition,
)
from great_expectations_provider.operators.constants import USER_AGENT_STR

if TYPE_CHECKING:
    import pyspark.sql as pyspark
    from airflow.utils.context import Context
    from great_expectations import ExpectationSuite
    from great_expectations.core.batch_definition import BatchDefinition
    from great_expectations.data_context import AbstractDataContext
    from great_expectations.expectations import Expectation
    from pandas import DataFrame
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame


class GXValidateDataFrameOperator(BaseOperator):
    """
    An operator to use Great Expectations to validate Expectations against a DataFrame in your Airflow DAG.

    Args:
        task_id: Airflow task ID. Alphanumeric name used in the Airflow UI and to name components in GX Cloud.
        configure_dataframe: A callable which returns the DataFrame to be validated.
        expect: An Expectation or ExpectationSuite to validate against the DataFrame. Available Expectations can
            be found at https://greatexpectations.io/expectations.
        result_format: control the verbosity of returned Validation Results. Possible values are
            "BOOLEAN_ONLY", "BASIC", "SUMMARY", "COMPLETE". Defaults to "SUMMARY". See
            https://docs.greatexpectations.io/docs/core/trigger_actions_based_on_results/choose_a_result_format
            for more information.
        context_type: accepts `ephemeral` or `cloud` to set the DataContext used by the Operator.
            Defaults to `ephemeral`, which does not persist results between runs.
            To save and view Validation Results in GX Cloud, use `cloud` and include
            GX Cloud credentials in your environment.
    """

    def __init__(
        self,
        configure_dataframe: Callable[
            [], DataFrame | pyspark.DataFrame | SparkConnectDataFrame
        ],
        expect: Expectation | ExpectationSuite,
        context_type: Literal["ephemeral", "cloud"] = "ephemeral",
        result_format: (
            Literal["BOOLEAN_ONLY", "BASIC", "SUMMARY", "COMPLETE"] | None
        ) = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.context_type = context_type
        self.dataframe = configure_dataframe()
        self.expect = expect
        self.result_format = result_format

    def execute(self, context: Context) -> dict:
        import great_expectations as gx
        from pandas import DataFrame

        gx_context = gx.get_context(
            mode=self.context_type,
            user_agent_str=USER_AGENT_STR,
        )
        if isinstance(self.dataframe, DataFrame):
            batch_definition = self._get_pandas_batch_definition(gx_context)
        elif type(self.dataframe).__name__ == "DataFrame":
            # if it's not pandas, but the classname is Dataframe, we assume spark
            batch_definition = self._get_spark_batch_definition(gx_context)
        else:
            raise ValueError(
                f"Unsupported dataframe type: {type(self.dataframe).__name__}"
            )

        batch_parameters = {
            "dataframe": self.dataframe,
        }
        result = run_validation_definition(
            task_id=self.task_id,
            expect=self.expect,
            batch_definition=batch_definition,
            result_format=self.result_format,
            batch_parameters=batch_parameters,
            gx_context=gx_context,
        )
        return result.describe_dict()

    def _get_spark_batch_definition(
        self, gx_context: AbstractDataContext
    ) -> BatchDefinition:
        return (
            gx_context.data_sources.add_or_update_spark(name=self.task_id)
            .add_dataframe_asset(name=self.task_id)
            .add_batch_definition_whole_dataframe(name=self.task_id)
        )

    def _get_pandas_batch_definition(
        self, gx_context: AbstractDataContext
    ) -> BatchDefinition:
        return (
            gx_context.data_sources.add_or_update_pandas(name=self.task_id)
            .add_dataframe_asset(name=self.task_id)
            .add_batch_definition_whole_dataframe(name=self.task_id)
        )
