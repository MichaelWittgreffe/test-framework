# Test Framework
## Introduction
A BDD test framework specifically designed for asserting the functionality of HTTP APIs.

## Adding Framework To Repository
1. Add the Makefile calls marked in `./Makefile` to your own projects Makefile, adding key-value secret passing on the command-line.
2. **OPTIONAL**: Write the custom authentication hooks class under `./generic_api` and add create handler to factory method. This class will need to inherit from `RequestRunner` base class and overload the `authenticate` and `set_request_token` methods. If you do this however the framework can no longer easily be replaced. You will need to ensure your new protocol contains the verb 'http' to be able to use the existing HTTP code. If you are adding a totally new protocol it is recommended you do this work in the main test-framework repo and not in your specific repository to allow others to benefit from your additions.
3. Call the following from the makefile to download, init and execute your tests:
    1. `make tf-download`
    2. `make tf-init`

## Writing Test Files
All tests use the Gherkin file format, and a "Given, When, Then" plain-text format for defining the tests. All files should be written in a `/features` directory at the root of your repository (created in command `make tf-download`) with the filename format `{name}.feature`, and can be executed with the command `make process-files`. An example of a feature file is provided in this README.

### Secrets and Parameters
All files contain the ability to provide secrets and parameters to requests and request templates. This is achieved by parsing the input with the Jinja2 Python3 framework. Any secrets you will be passing-in to the tests through the Makefile should be marked in full-capital letters and enclosed in '{{' '}}' braces, as in the below examples. Parameters defined in templates should be enclosed in '[[' ']]' braces, as in the below examples.

### Functionality Tests
Using the tag fixture `@api`, you are able to define a set of tests to ensure the functionality of an API endpoint meets the expected outcome. This is based on making the request with the given parameters and ensuring the response is validated against the given expected output. 

The first field to be defined is `Feature: {name}`, you can replace `{name}` for whatever you want.

The `Background` field is used to define default values for all requests, as well as to define your request templates. The templates are generic and do not contain a specific URL to contact. They follow a JSON format, allowing you to specify the Method, Query Params, Headers and Body for an HTTP request. If you add additional protocols, they should continue to use this JSON format but with the relevant fields. 

The `Scenario` fields are used to define your tests. The following statements are supported:

- **When:** `User makes {authenticated} {request_type} request {request_template_name} to endpoint {endpoint} containing`: This is the statement to make a request, you can add a table below this statement with the headers `label` and `values` to replace any templated values in your request template
    - `authenticated`: Use the string `"authenticated"` to make use of the authentication hooks
    - `request_type`: Replace this with "http" for the default supported protocol, or replace with your custom protocol
    - `request_template_name`: Replace this with the name of the template you would like to use for this request, defined in the `Background`
    - `endpoint`: Replace this with the URL to contact for this request
- **Then:** `The response Status Code is {status_code}`: This is an assertion of fact after a request has been made, ensures that the returned status code is the same as the status code you expect
- **Then:** `The {data_type} response body includes`: This is an assertion that the returned response body of `data_type` (e.g. `"json"`) includes the fields defined in a table (with the header `label`), this will make use of dot-paths to traverse a JSON structure (i.e. `foo.bar` references the data at position`{"foo": {"bar": 1234}}`), also includes support for JSON arrays by using an index integer in a dot-path. The `includes` keyword in the context of this framework means "ensure the field exists, ignore the data value".
- **Then:** `The {data_type} response body contains`: This is an assertion that the returned response body of `data_type` (e.g. `"json"`) includes the fields and values defined in a table (with the headers `label` and `values`), this will make use of dot-paths to traverse a JSON structure, also includes support for JSON arrays by using an index integer in a dot-path. The `contains` keyword in the context of this framework means "ensure the data field exists, and the data value matches my specification".
- **Then:** `The {req_type} response header includes`: As above, however on the response header instead of the body
- **Then:** `The {req_type} response header contains`: As above, however on the response header instead of the body
- **Then:** `the elapsed time is no more than {max_time} ms`: Assert that the total elapsed time for making the request and recieving the response is no longer than the specified millisecond value. The timings are taken immediatly before & after the request is made, and does not include any further evaluation in this time period.

#### Feature File Example

``` gherkin
@api
Feature: App
    Background:
        Given the following default values
            | label     | values                                |
            | Auth URL  | http://localhost:6006/api/v1/login    |
            | Username  | {{USERNAME}}                          |
            | Password  | {{PASSWORD}}                          |
        Given a request template test_template containing
        """
        {
            "method": "GET",
            "query_params": {
                "login": "true"
            }
        }
        """
        Given a request template example_template containing
        """
        {
            "method": "PUT",
            "headers": {
                "X-Tenant-ID": "1"
            },
            "body": {
                "value_1": "[[VALUE_1]]",
                "value_2": "[[VALUE_2]]"
            }
        }
        """

    Scenario: Test Endpoint
        When user makes un-authenticated http request test_template to endpoint http://localhost:6006/api/v1/test containing
        Then the response Status Code is 200

    Scenario: Example Endpoint
        When user makes authenticated example_http request example_template to endpoint http://localhost:6006/api/v1/example containing
            | label     | values    |
            | VALUE_1   | data_1    |
            | VALUE_2   | data_2    |
        Then the response Status Code is 201
        And the elapsed time is no more than 30 ms
        And the json response body includes
            | label             |
            | example.data.path |
        And the json response body contains
            | label                     | values    |
            | example.data.array.0.id   | 5         |
        And the http response header includes
            | label             |
            | X-Example-Field   |
        And the http response header contains
            | label             | values        |
            | X-Example-Field-2 | example_data  |
```