from behave.runner import Context
from behave import given


@given('The following default values')
def populate_default_values(context: Context) -> None:
    "adds the default values table to the context.default_values"
    if context is None:
        raise RuntimeError("Context Is None")

    if not hasattr(context, 'default_values'):
        context.default_values = {}

    if context.table is not None:
        for row in context.table:
            context.default_values[row["label"]] = row["values"]
