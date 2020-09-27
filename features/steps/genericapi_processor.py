import os
import json

from behave.runner import Context

from generic_api.factory import request_factory
from features.steps.support.templator import populate_template
from features.steps.processor_utils import get_dot_path_data, get_current_time_ms


@given('a request template {req_name} containing')  # type: ignore
def add_request_template(context: Context, req_name: str) -> None:
    "adds the request template to the request.templates"
    if not len(req_name):
        raise ValueError("req_name Is Empty")

    if not hasattr(context, 'templates'):
        context.templates = {}

    context.templates[req_name] = context.text


@when('User makes {authenticated} {request_type} request {request_template_name} to endpoint {endpoint} containing')  # type: ignore
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

    string_req_data = context.templates[request_template_name]

    if request_type.lower().find("http") > -1:
        return make_http_request(context, request_type, string_req_data, endpoint, auth_enabled, body_values)


def make_http_request(context: Context, protocol: str, string_req_data: str, endpoint: str, auth_enabled: bool, body_values: dict) -> None:
    "make an HTTP request through the GenericAPI"
    req_data = json.loads(string_req_data)
    method = req_data["method"].upper()

    if "query_params" in req_data:
        query_params = req_data["query_params"]
    else:
        query_params = {}

    if "body" in req_data:
        parsed_body = json.loads(populate_template(json.dumps(req_data["body"]), body_values))

        if "content_type" in req_data:
            content_type = req_data["content_type"]
        else:
            # safe default for most cases
            content_type = "application/json"
    else:
        parsed_body = {}
        content_type = ""

    if "headers" in req_data:
        headers = req_data["headers"]
    else:
        headers = {}

    req_run = request_factory(protocol, context.default_values['Auth URL'], context.default_values['Username'], context.default_values['Password'])

    # make the request
    context.start_time = get_current_time_ms()
    resp_body, resp_headers, resp_status_code, resp_err = req_run.run_request(method, endpoint, content_type, parsed_body, query_params, headers, auth_enabled)
    context.end_time = get_current_time_ms()

    # set context values or throw the error
    if len(resp_err):
        raise RuntimeError(f"Request Error: {resp_err}")

    context.response_body = resp_body
    context.response_headers = resp_headers
    context.response_status_code = resp_status_code


@then('The response Status Code is {status_code}')  # type: ignore
def validate_status_code(context: Context, status_code: str) -> None:
    if int(status_code) != context.response_status_code:
        raise ValueError(f"Returned Status Code Is Not Equal To Requested. Resp: {context.response_status_code}; Req: {int(status_code)}")


@then('The {data_type} response body includes')  # type: ignore
def validate_body_includes(context: Context, data_type: str) -> None:
    "validate the body includes the given paths (does not validate data)"
    for row in context.table:
        # exception raised from method if the request field does not exist
        dot_path = row["label"]
        data = get_dot_path_data(context.response_body, dot_path, data_type)

        if 'save_value' in row and row['save_value'] in ['True', 'true', 'Yes', 'yes', '1']:
            if not hasattr(context, 'saved_results'):
                context.saved_results = {}
            context.saved_results[dot_path] = data


@then('The {data_type} response body contains')  # type: ignore
def validate_body_contains(context: Context, data_type: str) -> None:
    "validate the body includes the given path with the given data associated"
    for row in context.table:
        # exception raised from method if the request field does not exist
        dot_path = row["label"]
        expected_data = row["values"]
        data = get_dot_path_data(context.response_body, dot_path, data_type)

        if str(data) != str(expected_data):
            raise ValueError(f"Data Does Not Match; Wanted: {expected_data}; Got: {data}")

        if 'save_value' in row and row['save_value'] in ['True', 'true', 'Yes', 'yes', '1']:
            if not hasattr(context, 'saved_results'):
                context.saved_results = {}
            context.saved_results[dot_path] = data


@then('The {req_type} response header includes')  # type: ignore
def validate_header_includes(context: Context, req_type: str):
    "validate the header includes the given fields (does not validate data)"
    for row in context.table:
        field_name = row['label']
        if field_name not in context.response_headers:
            raise ValueError(f"{field_name} Not Found In Response Headers")


@then('The {req_type} response header contains')  # type: ignore
def validate_header_contains(context: Context, req_type: str) -> None:
    "validate the header includes the given fields with the given associated values"
    for row in context.table:
        field_name = row['label']

        if field_name not in context.response_headers:
            raise ValueError(f"{field_name} Not Found In Response Headers")

        expected_field_value = row['values']
        field_value = context.response_headers[field_name]

        if str(expected_field_value) != str(field_value):
            raise ValueError(f"{field_name} Is Not Equal; Wanted: {expected_field_value}; Got: {field_value}")


@then('the elapsed time is no more than {max_time} ms')  # type: ignore
def validate_request_time(context: Context, max_time: str) -> None:
    "ensures the time taken for the request is no longer than the given millisecond value"
    elapsed_time = context.end_time - context.start_time

    if elapsed_time > int(max_time):
        raise RuntimeError(f"Request Took Too Long; Took: {elapsed_time}ms; Expected: {max_time}ms")
