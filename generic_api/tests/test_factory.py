from unittest import main, mock, TestCase

from generic_api.factory import request_factory
from generic_api.request_runner import RequestRunner
from generic_api.example_request_runner import ExampleRequestRunner


class TestRequestFactory(TestCase):
    "test class for the method 'request_factory'"

    def test_valid_1(self):
        "succesfully create a base class, no-auth request object"
        result = request_factory("HtTp", "http://localhost/login", "user", "pass")

        self.assertIsInstance(result, RequestRunner)

    def test_valid_2(self):
        "succesfully create the example derived object, auth details are empty to ensure these are just passed, not checked by the factory"
        result = request_factory("http_example", "", "", "")

        self.assertIsInstance(result, RequestRunner)
        self.assertIsInstance(result, ExampleRequestRunner)

    def test_invalid_1(self):
        "requested unsupported type create"
        with self.assertRaises(TypeError):
            request_factory("unsupported type", "", "", "")


if __name__ == "__main__":
    main()
