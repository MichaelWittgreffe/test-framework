import os
import json
from typing import Dict, Any

from behave.runner import Context
from behave import given, when, then
from jinja2 import Template

from generic_api.factory import request_factory
from generic_api.request_runner import RequestRunner
from features.steps.processor_utils import get_dot_path_data, get_current_time_ms


def populate_template(template: str, input_values: dict) -> str:
    "populate template renders a given Jinja2 template string with the given input_values"
    if not len(input_values):
        return template

    return Template(template).render(input_values)


@given('a request template {req_name} containing')
def add_request_template(context: Context, req_name: str) -> None:
    "adds the request template to the request.templates"
    if not len(req_name):
        raise ValueError("req_name Is Empty")

    if not hasattr(context, 'templates'):
        context.templates = {}

    context.templates[req_name] = context.text


@when('User makes {authenticated} {request_type} request {request_template_name} to endpoint {endpoint} containing')
def make_template_request(context: Context, authenticated: str, request_type: str, request_template_name: str, endpoint: str):
    "get the template, populate values from table, post results to context"
    body_values = {}

    if context.table is not None:
        for row in context.table:
            body_values[row["label"]] = row["values"]

    if authenticated.lower() == "authenticated":
        auth_enabled = True
    else:
        auth_enabled = False

    string_req_data: str = context.templates[request_template_name]

    if request_type.lower().find("http") > -1:
        return _make_http_request(context, request_type, string_req_data, endpoint, auth_enabled, body_values)


def _make_http_request(context: Context, protocol: str, string_req_data: str, endpoint: str, auth_enabled: bool, body_values: dict) -> None:
    "make an HTTP request through the GenericAPI"
    req_data: Dict[str, Any] = json.loads(string_req_data)

    if "method" not in req_data:
        raise ValueError("No Method In Template")

    method: str = req_data["method"].upper()

    if "query_params" in req_data:
        query_params = req_data["query_params"]
    else:
        query_params = {}

    if "headers" in req_data:
        headers = req_data["headers"]
    else:
        headers = {}

    if "body" in req_data:
        parsed_body = json.loads(
            populate_template(
                json.dumps(req_data["body"]),
                body_values
            )
        )

        if "content_type" in req_data:
            content_type = req_data["content_type"]
        elif "Content-Type" in headers:
            content_type = headers["Content-Type"]
        else:
            # safe default for most cases
            content_type = "application/json"
    else:
        parsed_body = {}
        content_type = ""

    if auth_enabled:
        for field_to_check in ("Auth URL", "Username", "Password"):
            if field_to_check not in context.default_values:
                raise ValueError(f"Authenticated Request Required, But Default Value {field_to_check} Is Missing")

        auth_url: str = context.default_values['Auth URL']
        username: str = context.default_values['Username']
        password: str = context.default_values['Password']
    else:
        auth_url = ""
        username = ""
        password = ""

    req_run: RequestRunner = request_factory(protocol, auth_url, username, password)

    # make the request
    try:
        context.start_time = get_current_time_ms()
        resp_body, resp_headers, resp_status_code = req_run.run_request(method, endpoint, content_type, parsed_body, query_params, headers, auth_enabled)
        context.end_time = get_current_time_ms()

        context.response_body = resp_body
        context.response_headers = resp_headers
        context.response_status_code = resp_status_code
    except Exception as ex:
        raise RuntimeError(f"Request Error: {ex}")


@then('The response Status Code is {status_code}')
def validate_status_code(context: Context, status_code: str) -> None:
    if not hasattr(context, "response_status_code"):
        raise RuntimeError("Response Status Code Not Found")

    if int(status_code) != context.response_status_code:
        raise ValueError(f"Returned Status Code Is Not Equal To Requested. Resp: {context.response_status_code}; Req: {int(status_code)}")


@then('The {data_type} response body includes')
def validate_body_includes(context: Context, data_type: str) -> None:
    "validate the body includes the given paths (does not validate data)"
    if not hasattr(context, "response_body"):
        raise RuntimeError("Context Response Body Not Found")

    for row in context.table:
        # exception raised from method if the request field does not exist
        if "label" not in row:
            raise ValueError("Table Formatting Incorrect: Missing Header 'label'")

        dot_path = row["label"]
        data = get_dot_path_data(context.response_body, dot_path, data_type)

        if 'save_value' in row and row['save_value'] in ['True', 'true', 'Yes', 'yes', '1']:
            if not hasattr(context, 'saved_results'):
                context.saved_results = {}
            context.saved_results[dot_path] = data


@then('The {data_type} response body contains')
def validate_body_contains(context: Context, data_type: str) -> None:
    "validate the body includes the given path with the given data associated"
    if not hasattr(context, "response_body"):
        raise RuntimeError("Context Response Body Not Found")

    for row in context.table:
        # exception raised from method if the request field does not exist
        if "label" not in row or "values" not in row:
            raise ValueError("Table Formatting Incorrect: Missing Headers 'label' Or 'values'")

        dot_path = row["label"]
        expected_data = row["values"]
        data = get_dot_path_data(context.response_body, dot_path, data_type)

        if str(data) != str(expected_data):
            raise ValueError(f"Data Does Not Match; Wanted: {expected_data}; Got: {data}")

        if 'save_value' in row and row['save_value'] in ['True', 'true', 'Yes', 'yes', '1']:
            if not hasattr(context, 'saved_results'):
                context.saved_results = {}
            context.saved_results[dot_path] = data


@then('The {req_type} response header includes')
def validate_header_includes(context: Context, req_type: str):
    "validate the header includes the given fields (does not validate data)"
    if not hasattr(context, "response_headers"):
        raise RuntimeError("Context Response Headers Not Found")

    for row in context.table:
        if "label" not in row:
            raise ValueError("Table Formatting Incorrect: Missing Header 'label'")

        field_name = row['label']
        if field_name not in context.response_headers:
            raise ValueError(f"{field_name} Not Found In Response Headers")


@then('The {req_type} response header contains')
def validate_header_contains(context: Context, req_type: str) -> None:
    "validate the header includes the given fields with the given associated values"
    if not hasattr(context, "response_headers"):
        raise RuntimeError("Context Response Headers Not Found")

    for row in context.table:
        if "label" not in row or "values" not in row:
            raise ValueError("Table Formatting Incorrect: Missing Headers 'label' Or 'values'")

        field_name = row['label']

        if field_name not in context.response_headers:
            raise ValueError(f"{field_name} Not Found In Response Headers")

        expected_field_value = row['values']
        field_value = context.response_headers[field_name]

        if str(expected_field_value) != str(field_value):
            raise ValueError(f"{field_name} Is Not Equal; Wanted: {expected_field_value}; Got: {field_value}")


@then('the elapsed time is no more than {max_time} ms')
def validate_request_time(context: Context, max_time: str) -> None:
    "ensures the time taken for the request is no longer than the given millisecond value"
    if int(max_time) <= 0:
        raise ValueError("Invalid max_time Value")

    if not hasattr(context, "end_time") or not hasattr(context, "start_time"):
        raise RuntimeError("end_time Or start_time Not Set On Context")

    elapsed_time: int = context.end_time - context.start_time

    if elapsed_time > int(max_time):
        raise ValueError(f"Request Took Too Long; Took: {elapsed_time}ms; Expected: {max_time}ms")
