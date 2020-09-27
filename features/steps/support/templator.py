from jinja2 import Template


def populate_template(template: str, input_values: dict) -> str:
    "populate template renders a given Jinja2 template string with the given input_values"
    template_obj = Template(template)
    return template_obj.render(input_values)
