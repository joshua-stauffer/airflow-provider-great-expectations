from __future__ import annotations
from typing import Callable, Literal, TYPE_CHECKING

from airflow.models import BaseOperator, BaseOperatorLink, Connection, XCom


if TYPE_CHECKING:
    from great_expectations.data_context import AbstractDataContext, FileDataContext
    from great_expectations import Checkpoint
    from great_expectations.core.batch import BatchParameters
    from airflow.utils.context import Context


class ValidateCheckpointOperator(BaseOperator):
    def __init__(
        self,
        configure_checkpoint: Callable[[AbstractDataContext], Checkpoint],
        batch_parameters: BatchParameters | None = None,
        context_type: Literal["ephemeral", "cloud", "file"] = "ephemeral",
        configure_file_data_context: Callable[[], FileDataContext] | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        import great_expectations as gx

        if batch_parameters is None:
            self.batch_parameters = {}
        else:
            self.batch_parameters = batch_parameters
        if context_type == "file" and not configure_file_data_context:
            raise ValueError(
                "Parameter `configure_file_data_context` must be specified if `context_type` is `file`"
            )

        if context_type == "file":
            self.context = configure_file_data_context()
        else:
            self.context = gx.get_context(mode=context_type)
        self.checkpoint = configure_checkpoint(self.context)

    def execute(self, context: Context) -> dict:
        result = self.checkpoint.run(batch_parameters=self.batch_parameters)
        print(result)
        return result.dict()
