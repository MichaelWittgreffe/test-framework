from behave.runner import Context


@given('The following default values')
def populate_default_values(context: Context):
    "adds the default values table to the context.default_values"
    if not hasattr(context, 'default_values'):
        context.default_values = {}

    for row in context.table:
        context.default_values[row["label"]] = row["values"]
