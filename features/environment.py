import os
import json
from typing import Dict, Callable

from behave.fixture import fixture, use_fixture_by_tag

from generic_api.template_constants import template_constants


@fixture
def populate_template_constants(context) -> bool:
    "adds the template constants to the context"
    context.templates = template_constants
    return True


def after_scenario(context, scenario):
    context.templates = {}
    context.default_values = {}


def before_tag(context, tag):
    if tag.startswith("constants"):
        return use_fixture_by_tag(tag, context, fixture_registry)


fixture_registry: Dict[str, Callable] = {
    "constants": populate_template_constants,
}
