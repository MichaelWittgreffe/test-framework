# Test Framework
## Introduction
Development area for the Content Processing team's Test Framework.

## Adding Framework To Repository
1. Add the Makefile calls marked in ```./Makefile``` to your own projects Makefile, adding key-value secret passing on the command-line.
2. **OPTIONAL**: Write the custom authentication hooks class under ```./generic_api``` and add create handler to factory method. This class will need to inherit from ```RequestRunner``` base class and overload the ```authenticate``` and ```set_request_token``` methods. If you do this however the framework can no longer easily be replaced. You will need to ensure your new protocol contains the verb 'http' to be able to use the existing HTTP code. If you are adding a totally new protocol it is recommended you do this work in the main test-framework repo and not in your specific repository to allow others to benefit from your additions.
3. Call the following from the makefile to download, init and execute your tests:
    - ```make all-tf```
    - or:
        1. ```make tf-download```
        2. ```make tf-init```
        3. ```make tf-process-files```

## Writing Test Files
### Secrets and Parameters
All files contain the ability to provide secrets and parameters to requests and request templates. This is achieved by parsing the input with the Jinja2 Python3 framework. Any secrets you will be passing-in to the tests through the Makefile should be marked in full-capital letters and enclosed in '{{' '}}' braces, as in the below examples. Parameters defined in templates should be enclosed in '[[' ']]' braces, as in the below examples.

### Functionality Tests
Using the tag fixture ```@api```, you are able to define a set of tests to ensure the functionality of an API endpoint meets the expected outcome. This is based on making the request with the given parameters and ensuring the response is validated against the given expected output. An example feature file would be as below:

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