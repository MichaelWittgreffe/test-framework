from unittest import mock, main, TestCase
import json

from behave.runner import Context

from features.steps import genericapi_processor as genapi


class TestPopulateTemplate(TestCase):
    "test class for the method 'genapi.populate_template'"

    def test_valid_1(self):
        "succesfully populate the given template with the given values"
        template = "{{HELLO}} World"
        result = genapi.populate_template(template, {"HELLO": "Hello"})
        self.assertEqual(result, "Hello World")

    def test_valid_2(self):
        "no values to actually render"
        template = "Hello World"
        result = genapi.populate_template(template, {})
        self.assertEqual(result, "Hello World")

    def test_invalid_1(self):
        "blank template given"


class TestAddRequestTemplate(TestCase):
    "test class for the method 'genapi.add_request_template'"

    def test_valid_1(self):
        "succesfully add a request template to the context"
        m_context = Context(mock.MagicMock())
        m_context.text = "template"

        self.assertIsNone(genapi.add_request_template(m_context, "test_req"))

        self.assertTrue(hasattr(m_context, "templates"))
        self.assertIsInstance(m_context.templates, dict)
        self.assertIn("test_req", m_context.templates)
        self.assertEqual(m_context.templates["test_req"], "template")

    def test_invalid_1(self):
        "given request name is invalid"
        with self.assertRaises(ValueError):
            genapi.add_request_template(mock.MagicMock(), "")


class TestMakeTemplateRequest(TestCase):
    "test class for the method 'make_template_request'"

    @mock.patch("features.steps.genericapi_processor.request_factory", return_value=mock.MagicMock())
    def test_valid_1(self, m_factory):
        "succesfully make a template request, POST method, auth enabled"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "HELLO", "values": "hello"}, {"label": "WORLD", "values": "world"}]
        m_context.default_values = {
            "Auth URL": "http://localhost/auth/login",
            "Username": "user",
            "Password": "pass",
        }
        m_context.templates = {
            "test_template": json.dumps(
                {
                    "method": "POST",
                    "content_type": "application/json",
                    "headers": {},
                    "body": {"{{HELLO}}": "{{WORLD}}"},
                }
            )
        }
        m_factory.return_value.run_request.return_value = (None, {}, 201)

        self.assertIsNone(genapi.make_template_request(m_context, "authenticated", "http", "test_template", "http://localhost/blob"))

        self.assertTrue(hasattr(m_context, "start_time"))
        self.assertTrue(hasattr(m_context, "end_time"))
        self.assertTrue(hasattr(m_context, "response_body"))
        self.assertTrue(hasattr(m_context, "response_headers"))
        self.assertTrue(hasattr(m_context, "response_status_code"))
        self.assertIsNone(m_context.response_body)
        self.assertDictEqual(m_context.response_headers, {})
        self.assertEqual(m_context.response_status_code, 201)

    @mock.patch("features.steps.genericapi_processor.request_factory", return_value=mock.MagicMock())
    def test_valid_2(self, m_factory):
        "succesfully make a template request, GET method, auth disabled"
        m_context = Context(mock.MagicMock())
        m_context.default_values = {}
        m_context.templates = {
            "test_template": json.dumps(
                {
                    "method": "GET",
                    "query_params": {"bar": "foo"},
                }
            )
        }
        m_factory.return_value.run_request.return_value = ({"foo": "bar"}, {}, 200)

        self.assertIsNone(genapi.make_template_request(m_context, "un-authenticated", "http", "test_template", "http://localhost/blob"))

        self.assertTrue(hasattr(m_context, "start_time"))
        self.assertTrue(hasattr(m_context, "end_time"))
        self.assertTrue(hasattr(m_context, "response_body"))
        self.assertTrue(hasattr(m_context, "response_headers"))
        self.assertTrue(hasattr(m_context, "response_status_code"))
        self.assertDictEqual(m_context.response_body, {"foo": "bar"})
        self.assertDictEqual(m_context.response_headers, {})
        self.assertEqual(m_context.response_status_code, 200)

    @mock.patch("features.steps.genericapi_processor.request_factory", return_value=mock.MagicMock())
    def test_valid_3(self, m_factory):
        "succesfully make a template request, POST method, auth enabled, content-type defined in headers rather than standalone"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "HELLO", "values": "hello"}, {"label": "WORLD", "values": "world"}]
        m_context.default_values = {
            "Auth URL": "http://localhost/auth/login",
            "Username": "user",
            "Password": "pass",
        }
        m_context.templates = {
            "test_template": json.dumps(
                {
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "body": {"{{HELLO}}": "{{WORLD}}"},
                }
            )
        }
        m_factory.return_value.run_request.return_value = (None, {}, 201)

        self.assertIsNone(genapi.make_template_request(m_context, "authenticated", "http", "test_template", "http://localhost/blob"))

        self.assertTrue(hasattr(m_context, "start_time"))
        self.assertTrue(hasattr(m_context, "end_time"))
        self.assertTrue(hasattr(m_context, "response_body"))
        self.assertTrue(hasattr(m_context, "response_headers"))
        self.assertTrue(hasattr(m_context, "response_status_code"))
        self.assertIsNone(m_context.response_body)
        self.assertDictEqual(m_context.response_headers, {})
        self.assertEqual(m_context.response_status_code, 201)

    @mock.patch("features.steps.genericapi_processor.request_factory", return_value=mock.MagicMock())
    def test_valid_4(self, m_factory):
        "succesfully make a template request, POST method, auth disabled, uses default content type"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "HELLO", "values": "hello"}, {"label": "WORLD", "values": "world"}]
        m_context.default_values = {
            "Auth URL": "http://localhost/auth/login",
            "Username": "user",
            "Password": "pass",
        }
        m_context.templates = {
            "test_template": json.dumps(
                {
                    "method": "POST",
                    "body": {"{{HELLO}}": "{{WORLD}}"},
                }
            )
        }
        m_factory.return_value.run_request.return_value = (None, {}, 201)

        self.assertIsNone(genapi.make_template_request(m_context, "un-authenticated", "http", "test_template", "http://localhost/blob"))

        self.assertTrue(hasattr(m_context, "start_time"))
        self.assertTrue(hasattr(m_context, "end_time"))
        self.assertTrue(hasattr(m_context, "response_body"))
        self.assertTrue(hasattr(m_context, "response_headers"))
        self.assertTrue(hasattr(m_context, "response_status_code"))
        self.assertIsNone(m_context.response_body)
        self.assertDictEqual(m_context.response_headers, {})
        self.assertEqual(m_context.response_status_code, 201)

    @mock.patch("features.steps.genericapi_processor.request_factory", return_value=mock.MagicMock())
    def test_invalid_1(self, m_factory):
        "exception whilst running request"
        m_context = Context(mock.MagicMock())
        m_context.default_values = {}
        m_context.templates = {
            "test_template": json.dumps(
                {
                    "method": "GET",
                    "query_params": {"bar": "foo"},
                }
            )
        }
        m_factory.return_value.run_request.side_effect = ConnectionError("Test Error")

        with self.assertRaises(RuntimeError):
            genapi.make_template_request(m_context, "un-authenticated", "http", "test_template", "http://localhost/blob")

    def test_invalid_2(self):
        "auth request requested, but values not provided"
        m_context = Context(mock.MagicMock())
        m_context.default_values = {}
        m_context.templates = {
            "test_template": json.dumps(
                {
                    "method": "GET",
                    "query_params": {"bar": "foo"},
                }
            )
        }

        with self.assertRaises(ValueError):
            genapi.make_template_request(m_context, "authenticated", "http", "test_template", "http://localhost/blob")

    def test_invalid_3(self):
        "method not provided in template"
        m_context = Context(mock.MagicMock())
        m_context.default_values = {}
        m_context.templates = {
            "test_template": json.dumps(
                {
                    "query_params": {"bar": "foo"},
                }
            )
        }

        with self.assertRaises(ValueError):
            genapi.make_template_request(m_context, "authenticated", "http", "test_template", "http://localhost/blob")


class TestValidateStatusCode(TestCase):
    "test class for the method 'genapi.validate_status_code'"

    def test_valid_1(self):
        "succesfully validate the given status codes"
        m_context = Context(mock.MagicMock())
        m_context.response_status_code = 200
        self.assertIsNone(genapi.validate_status_code(m_context, 200))

    def test_invalid_1(self):
        "status code does not match"
        m_context = Context(mock.MagicMock())
        m_context.response_status_code = 500

        with self.assertRaises(ValueError):
            genapi.validate_status_code(m_context, 200)

    def test_invalid_2(self):
        "response status code not set on context"
        with self.assertRaises(RuntimeError):
            genapi.validate_status_code(Context(mock.MagicMock()), 200)


class TestValidateBodyIncludes(TestCase):
    "test class for the method 'genapi.validate_body_includes'"

    def test_valid_1(self):
        "validate body field succesfully, saved response value"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "foo.bar", "save_value": "yes"}]
        m_context.response_body = {"foo": {"bar": 1234}}

        self.assertIsNone(genapi.validate_body_includes(m_context, "json"))

        self.assertTrue(hasattr(m_context, "saved_results"))
        self.assertIn("foo.bar", m_context.saved_results)
        self.assertEqual(m_context.saved_results["foo.bar"], 1234)

    def test_valid_2(self):
        "validate body field succesfully, do not save response value"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "foo.bar", "save_value": "no"}]
        m_context.response_body = {"foo": {"bar": 1234}}

        self.assertIsNone(genapi.validate_body_includes(m_context, "json"))

        self.assertFalse(hasattr(m_context, "saved_results"))

    def test_invalid_1(self):
        "requested dot path cannot be found"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "foo.bar", "save_value": "no"}]
        m_context.response_body = {}

        with self.assertRaises(ValueError):
            genapi.validate_body_includes(m_context, "json")

    def test_invalid_2(self):
        "invalid data type given"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "foo.bar", "save_value": "no"}]
        m_context.response_body = {"foo": {"bar": 1234}}

        with self.assertRaises(TypeError):
            genapi.validate_body_includes(m_context, "unsupported data type")

    def test_invalid_3(self):
        "context missing response body"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "foo.bar", "save_value": "no"}]

        with self.assertRaises(RuntimeError):
            genapi.validate_body_includes(m_context, "json")


class TestValidateBodyContains(TestCase):
    "test class for the method 'genapi.validate_body_contains'"

    def test_valid_1(self):
        "succesfully validate the response body contains given data"
        m_context = Context(mock.MagicMock())
        m_context.table = [
            {"label": "foo.bar", "values": 1234, "save_value": "yes"},
            {"label": "integer", "values": 1234, "save_value": "no"},
            {"label": "string", "values": "blob", "save_value": "no"},
            {"label": "float", "values": 1234.56, "save_value": "no"},
            {"label": "none", "values": None, "save_value": "no"},
            {"label": "array", "values": [1, 2], "save_value": "no"},
            {"label": "object", "values": {"foo": "bar"}, "save_value": "no"},
        ]
        m_context.response_body = {
            "foo": {
                "bar": 1234,
            },
            "integer": 1234,
            "string": "blob",
            "float": 1234.56,
            "none": None,
            "array": [1, 2],
            "object": {"foo": "bar"},
        }

        self.assertIsNone(genapi.validate_body_contains(m_context, "json"))
        self.assertTrue(hasattr(m_context, "saved_results"))
        self.assertIn("foo.bar", m_context.saved_results)
        self.assertEqual(m_context.saved_results["foo.bar"], 1234)

    def test_invalid_1(self):
        "requested data does not match"
        m_context = Context(mock.MagicMock())
        m_context.table = [
            {"label": "foo.bar", "values": 1234, "save_value": "no"},
        ]
        m_context.response_body = {
            "foo": {
                "bar": "foobar",
            },
        }

        with self.assertRaises(ValueError):
            genapi.validate_body_contains(m_context, "json")

    def test_invalid_2(self):
        "no response body found on context"
        m_context = Context(mock.MagicMock())
        m_context.table = [
            {"label": "foo.bar", "values": 1234, "save_value": "no"},
        ]

        with self.assertRaises(RuntimeError):
            genapi.validate_body_contains(m_context, "json")


if __name__ == "__main__":
    main()
