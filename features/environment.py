import os
import json
from typing import Dict, Callable

from behave.fixture import fixture, use_fixture_by_tag
from behave.runner import Context
from behave.model import Tag, Scenario

from generic_api.template_constants import template_constants


@fixture
def populate_template_constants(context: Context) -> bool:
    "adds the template constants to the context"
    if context is None:
        raise RuntimeError("Context Is None")

    context.templates = template_constants
    return True


def after_scenario(context: Context, scenario: Scenario):
    "runs after a scenario has finished, used to reset values"
    if context is None:
        raise RuntimeError("Context Is None")

    context.templates = {}
    context.default_values = {}


def before_tag(context: Context, tag: Tag):
    if context is None or tag is None:
        raise RuntimeError("Context Or Tag Is None")

    if tag.startswith("constants"):
        return use_fixture_by_tag(tag, context, fixture_registry)


fixture_registry: Dict[str, Callable] = {
    "constants": populate_template_constants,
}
