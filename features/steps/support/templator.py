from jinja2 import Template


def populate_template(template: str, input_values: dict) -> str:
    "populate template renders a given Jinja2 template string with the given input_values"
    template = Template(template)
    return template.render(input_values)
