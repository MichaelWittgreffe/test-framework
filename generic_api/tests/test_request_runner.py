from unittest import main, mock, TestCase
import json

from generic_api.request_runner import RequestRunner


class TestRequestRunner(TestCase):
    "test class for RequestRunner"

    def test_valid_constructor_1(self):
        "succesfully construct the required fields"
        result = RequestRunner(auth_url="http://auth", username="user", password="pass")

        self.assertEqual(result.auth_url, "http://auth")
        self.assertEqual(result.username, "user")
        self.assertEqual(result.password, "pass")

        for method in ("GET", "PUT", "POST", "DELETE"):
            self.assertIn(method, result.supported_methods)

        for content_type in ("application/json", "application/json; charset=UTF-8"):
            self.assertIn(content_type, result.supported_content_types)
            entry = result.supported_content_types[content_type]
            self.assertIn("encode", entry)
            self.assertIn("decode", entry)

    def test_valid_authenticate_1(self):
        "ensure the base class method just returns an empty string"
        client = RequestRunner()
        self.assertEqual(client.authenticate(), "")

    def test_valid_set_request_token_1(self):
        "ensure the base class method just returns the given headers dict"
        client = RequestRunner()
        self.assertDictEqual(client.set_request_token({"foo": "bar"}, "token"), {"foo": "bar"})

    @mock.patch("generic_api.request_runner.requests.get", return_value=mock.MagicMock())
    @mock.patch("generic_api.request_runner.RequestRunner.authenticate", return_value="testauthtoken")
    def test_valid_get_request_1(self, m_token, m_get):
        "use the 'run_request' method to succesfully run a GET request"
        m_get.return_value.headers = {"Content-Type": "application/json"}
        m_get.return_value.text = json.dumps({"blob": "blib"})
        m_get.return_value.status_code = 200

        client = RequestRunner(auth_url="http://auth", username="user", password="pass")

        result_body, result_headers, result_status_code = client.run_request(
            "GET", "http://blob/blib", query_params={"foo": "bar"}, header_params={"bar": "foo"})

        self.assertDictEqual(result_body, {"blob": "blib"})
        self.assertDictEqual(result_headers, {"Content-Type": "application/json"})
        self.assertEqual(result_status_code, 200)

    @mock.patch("generic_api.request_runner.requests.get", return_value=mock.MagicMock())
    def test_valid_get_request_2(self, m_get):
        "use the 'run_request' method to succesfully run a GET request, no content-type returned, and no auth requested"
        m_get.return_value.headers = {}
        m_get.return_value.text = json.dumps({"blob": "blib"})
        m_get.return_value.status_code = 200

        client = RequestRunner()

        result_body, result_headers, result_status_code = client.run_request(
            "GET", "http://blob/blib", query_params={"foo": "bar"}, header_params={"bar": "foo"}, authenticate=False)

        self.assertDictEqual(result_body, {"blob": "blib"})
        self.assertDictEqual(result_headers, {})
        self.assertEqual(result_status_code, 200)

    @mock.patch("generic_api.request_runner.requests.get", return_value=mock.MagicMock())
    def test_valid_get_request_3(self, m_get):
        "use the 'run_request' method to succesfully run a GET request, no auth, no body returned"
        m_get.return_value.headers = {}
        m_get.return_value.status_code = 200

        client = RequestRunner()

        result_body, result_headers, result_status_code = client.run_request(
            "GET", "http://blob/blib", query_params={"foo": "bar"}, header_params={"bar": "foo"}, authenticate=False)

        self.assertIsNone(result_body)
        self.assertDictEqual(result_headers, {})
        self.assertEqual(result_status_code, 200)

    @mock.patch("generic_api.request_runner.requests.get", side_effect=ConnectionError("Test Error"))
    def test_invalid_get_request_1(self, m_get):
        "exception encountered executing request"
        client = RequestRunner()

        with self.assertRaises(RuntimeError):
            result_body, result_headers, result_status_code = client.run_request(
                "GET", "http://blob/blib", query_params={"foo": "bar"}, header_params={"bar": "foo"}, authenticate=False)

    @mock.patch("generic_api.request_runner.requests.post", return_value=mock.MagicMock())
    @mock.patch("generic_api.request_runner.RequestRunner.authenticate", return_value="testauthtoken")
    def test_valid_post_request_1(self, m_token, m_post):
        "succesfully execute a post request using the 'run_request' method"
        m_post.return_value.headers = {"Content-Type": "application/json"}
        m_post.return_value.text = json.dumps({"bar": "foo"})
        m_post.return_value.status_code = 200

        client = RequestRunner(auth_url="http://auth", username="user", password="pass")

        result_body, result_headers, result_status_code = client.run_request(
            "POST", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"})

        self.assertDictEqual(result_body, {"bar": "foo"})
        self.assertDictEqual(result_headers, {"Content-Type": "application/json"})
        self.assertEqual(result_status_code, 200)

    @mock.patch("generic_api.request_runner.requests.post", return_value=mock.MagicMock())
    def test_valid_post_request_2(self, m_post):
        "succesfully execute a post request using the 'run_request' method, no content type returned, no auth"
        m_post.return_value.headers = {}
        m_post.return_value.text = json.dumps({"bar": "foo"})
        m_post.return_value.status_code = 200

        client = RequestRunner()

        result_body, result_headers, result_status_code = client.run_request(
            "POST", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"}, authenticate=False)

        self.assertDictEqual(result_body, {"bar": "foo"})
        self.assertDictEqual(result_headers, {})
        self.assertEqual(result_status_code, 200)

    @mock.patch("generic_api.request_runner.requests.post", side_effect=ConnectionError("Test Error"))
    def test_invalid_post_request_1(self, m_post):
        "exception making request"
        client = RequestRunner()

        with self.assertRaises(RuntimeError):
            result_body, result_headers, result_status_code = client.run_request(
                "POST", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"}, authenticate=False)

    @mock.patch("generic_api.request_runner.requests.delete", return_value=mock.MagicMock())
    @mock.patch("generic_api.request_runner.RequestRunner.authenticate", return_value="testauthtoken")
    def test_valid_delete_request_1(self, m_token, m_get):
        "use the 'run_request' method to succesfully run a DELETE request"
        m_get.return_value.headers = {}
        m_get.return_value.status_code = 204

        client = RequestRunner(auth_url="http://auth", username="user", password="pass")

        result_body, result_headers, result_status_code = client.run_request(
            "DELETE", "http://blob/blib", query_params={"foo": "bar"}, header_params={"bar": "foo"})

        self.assertIsNone(result_body)
        self.assertDictEqual(result_headers, {})
        self.assertEqual(result_status_code, 204)

    @mock.patch("generic_api.request_runner.requests.delete", side_effect=ConnectionError("Test Error"))
    def test_invalid_delete_request_1(self, m_post):
        "exception making request"
        with self.assertRaises(RuntimeError):
            result_body, result_headers, result_status_code = RequestRunner().run_request(
                "DELETE", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"}, authenticate=False)

    @mock.patch("generic_api.request_runner.requests.put", return_value=mock.MagicMock())
    @mock.patch("generic_api.request_runner.RequestRunner.authenticate", return_value="testauthtoken")
    def test_valid_put_request_1(self, m_token, m_get):
        "use the 'run_request' method to succesfully run a DELETE request"
        m_get.return_value.headers = {}
        m_get.return_value.status_code = 201

        client = RequestRunner(auth_url="http://auth", username="user", password="pass")

        result_body, result_headers, result_status_code = client.run_request(
            "PUT", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"})

        self.assertIsNone(result_body)
        self.assertDictEqual(result_headers, {})
        self.assertEqual(result_status_code, 201)

    @mock.patch("generic_api.request_runner.requests.put", side_effect=ConnectionError("Test Error"))
    def test_invalid_put_request_1(self, m_post):
        "exception making request"
        with self.assertRaises(RuntimeError):
            result_body, result_headers, result_status_code = RequestRunner().run_request(
                "PUT", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"}, authenticate=False)

    def test_invalid_run_request_1(self):
        "returned auth token is empty"
        client = RequestRunner(auth_url="http://auth", username="user", password="pass")

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "GET", "http://blob/blib", query_params={"foo": "bar"}, header_params={"bar": "foo"})

    def test_invalid_run_request_2(self):
        "auth requested but auth details not supplied in constructor"
        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "GET", "http://blob/blib", query_params={"foo": "bar"}, header_params={"bar": "foo"})

    def test_invalid_run_request_3(self):
        "no content_type supplied as kwarg or in header"
        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "POST", "http://blob/blib", body={"foo": "bar"}, header_params={})

    def test_invalid_run_request_4(self):
        "invalid url given"
        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "POST", "", body={"foo": "bar"}, header_params={})

    def test_invalid_run_request_5(self):
        "invalid http method requested"
        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "UNSUPPORTED METHOD TYPE", "", body={"foo": "bar"}, header_params={})

    def test_invalid_run_request_6(self):
        "content_type not supported in body encode"
        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "POST", "http://blob/blib", body={"foo": "bar"}, header_params={}, content_type="UNSUPPORTED", authenticate=False)

    @mock.patch("generic_api.request_runner.requests.post", return_value=mock.MagicMock())
    def test_invalid_run_request_7(self, m_post):
        "content_type of response body is not supported"
        m_post.return_value.headers = {"Content-Type": "UNSUPPORTED"}
        m_post.return_value.text = json.dumps({"bar": "foo"})
        m_post.return_value.status_code = 200

        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "POST", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"}, authenticate=False)

    @mock.patch("generic_api.request_runner.json.dumps", side_effect=RuntimeError("Test Error"))
    def test_invalid_run_request_8(self, m_dumps):
        "invalid json given for body encode"
        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "POST", "http://blob/blib", body={"foo": "bar"}, header_params={}, content_type="application/json", authenticate=False)

    @mock.patch("generic_api.request_runner.requests.post", return_value=mock.MagicMock())
    def test_invalid_run_request_9(self, m_post):
        "invalid json returned in the response body for decode"
        m_post.return_value.headers = {"Content-Type": "application/json"}
        m_post.return_value.text = "asdfhaetrjaetrhaer"
        m_post.return_value.status_code = 200

        client = RequestRunner()

        with self.assertRaises(ValueError):
            result_body, result_headers, result_status_code = client.run_request(
                "POST", "http://blob/blib", body={"foo": "bar"}, header_params={"Content-Type": "application/json"}, authenticate=False)


if __name__ == "__main__":
    main()
