from unittest import main, mock, TestCase
from ..base_request_runner import RequestRunner


class TestRequestRunner(TestCase):
    """
    test class for the base RequestRunner class
    the private method edge cases are run on the GET/POST tests
    """

    def test_valid_constructor_1(self):
        "valid run of the constructor with data fields being setup"
        auth_url = "http://test.com/api"
        test_user = "username"
        test_pass = "password"
        runner = RequestRunner(auth_url=auth_url, username=test_user, password=test_pass)
        self.assertEqual(runner.auth_url, auth_url)
        self.assertEqual(runner.username, test_user)
        self.assertEqual(runner.password, test_pass)
        self.assertIn('GET', runner.supported_methods)
        self.assertIn('POST', runner.supported_methods)
        self.assertIn('PUT', runner.supported_methods)
        self.assertIn('DELETE', runner.supported_methods)
        self.assertIn('application/json', runner.supported_content_types)
        self.assertIn('application/json; charset=UTF-8', runner.supported_content_types)

    def test_valid_constructor_2(self):
        "valid run of the constructor without data fields being setup (no-auth)"
        runner = RequestRunner()
        self.assertEqual(runner.auth_url, '')
        self.assertEqual(runner.username, '')
        self.assertEqual(runner.password, '')
        self.assertIn('GET', runner.supported_methods)
        self.assertIn('POST', runner.supported_methods)
        self.assertIn('PUT', runner.supported_methods)
        self.assertIn('DELETE', runner.supported_methods)
        self.assertIn('application/json', runner.supported_content_types)
        self.assertIn('application/json; charset=UTF-8', runner.supported_content_types)

    def test_valid_authenticate_1(self):
        "ensures that the base authenticate method is not implemented"
        runner = RequestRunner()
        auth_token = runner.authenticate()
        self.assertFalse(len(auth_token))

    def test_valid_set_request_token_1(self):
        "ensures that the base set_request_token method is not implemented"
        runner = RequestRunner()
        result_header = runner.set_request_token({}, "auth_token")
        self.assertEqual({}, result_header)

    @mock.patch('generic_api.base_request_runner.requests.get', return_value=mock.MagicMock())
    def test_valid_run_request_get_1(self, m_get):
        "make a valid GET request with no authentication"
        method = "GET"
        url = "http://testendpoint.com"

        m_get.return_value.headers = {"Content-Type": "application/json"}
        m_get.return_value.status_code = 200
        m_get.return_value.text = "{\"test\": \"result\"}"

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request(method, url, authenticate=False)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"test": "result"})
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.get', return_value=mock.MagicMock())
    @mock.patch('generic_api.base_request_runner.RequestRunner.authenticate', return_value="AUTHTOKEN")
    def test_valid_run_request_get_2(self, m_authenticate, m_get):
        "make a valid GET request with authentication, content-type missing from response"
        method = "GET"
        url = "http://testendpoint.com"

        m_get.return_value.headers = {}
        m_get.return_value.status_code = 200
        m_get.return_value.text = "{\"test\": \"result\"}"
        m_get.return_value.json.return_value = {"test": "result"}

        runner = RequestRunner(auth_url="http://testendpoint.com/api/auth", username="username", password="password")
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request(method, url, authenticate=True)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"test": "result"})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.get', return_value=mock.MagicMock())
    def test_valid_run_request_get_3(self, m_get):
        "no response body is returned, expect to return an empty dict, no authentication"
        method = "GET"
        url = "http://testendpoint.com"

        m_get.return_value.headers = {}
        m_get.return_value.status_code = 200
        m_get.return_value.text = ""

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request(method, url, authenticate=False)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.get', return_value=mock.MagicMock())
    def test_invalid_run_request_get_1(self, m_get):
        "unsupported content type returned from server"
        method = "GET"
        url = "http://testendpoint.com"

        m_get.return_value.headers = {"Content-Type": "application/bob"}
        m_get.return_value.status_code = 200
        m_get.return_value.text = "this is a silly format made up for testing"

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request(method, url, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, {"Content-Type": "application/bob"})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.get', return_value=mock.MagicMock())
    def test_invalid_run_request_get_2(self, m_get):
        "exception occurs when decoding JSON response, this code runs because content-type is not in response header"
        method = "GET"
        url = "http://testendpoint.com"

        m_get.return_value.headers = {}
        m_get.return_value.status_code = 200
        m_get.return_value.text = "{\"INVALID_JSON\"}"
        m_get.return_value.json.side_effect = Exception("Invalid JSON")

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request(method, url, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.get', return_value=mock.MagicMock())
    def test_invalid_run_request_get_3(self, m_get):
        "exception occurs when decoding JSON response, this code runs when content-type is in the response header"
        method = "GET"
        url = "http://testendpoint.com"

        m_get.return_value.headers = {"Content-Type": "application/json"}
        m_get.return_value.status_code = 200
        m_get.return_value.text = "{\"INVALID_JSON\"}"

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request(method, url, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.get', side_effect=Exception("HTTP Test Exception"))
    def test_invalid_run_request_get_4(self, m_get):
        "exception occurs when making the HTTP request"
        method = "GET"
        url = "http://testendpoint.com"

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request(method, url, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, None)
        self.assertEqual(resp_status_code, -1)

    def test_invalid_run_request_get_5(self):
        "authentication requested, auth details not configured"
        with self.assertRaises(ValueError):
            runner = RequestRunner()
            resp_body, resp_header, resp_status_code, resp_err = runner.run_request("GET", "http://test.com", authenticate=True)

    @mock.patch('generic_api.base_request_runner.RequestRunner.authenticate', return_value="")
    def test_invalid_run_request_get_6(self, m_authenticate):
        "auth requested, no auth token returned"
        with self.assertRaises(ValueError):
            runner = RequestRunner(auth_url="http://test.com/auth", username="user", password="pass")
            resp_body, resp_header, resp_status_code, resp_err = runner.run_request("GET", "http://test.com", authenticate=True)

    def test_invalid_run_request_get_7(self):
        "requested HTTP method is not supported"
        with self.assertRaises(ValueError):
            runner = RequestRunner()
            resp_body, resp_header, resp_status_code, resp_err = runner.run_request("BLOB", "http://test.com", authenticate=False)

    @mock.patch('generic_api.base_request_runner.requests.post', return_value=mock.MagicMock())
    def test_valid_run_request_post_1(self, m_post):
        "make a valid POST request with no authentication"
        m_post.return_value.headers = {"Content-Type": "application/json"}
        m_post.return_value.status_code = 201
        m_post.return_value.text = "{\"Test\": \"Response\"}"

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"Test": "Response"})
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 201)

    @mock.patch('generic_api.base_request_runner.requests.post', return_value=mock.MagicMock())
    @mock.patch('generic_api.base_request_runner.RequestRunner.authenticate', return_value="AUTHTOKEN")
    def test_valid_run_request_post_2(self, m_authenticate, m_post):
        "make a valid POST request with authentication and response doesn't include content-type"
        m_post.return_value.headers = {}
        m_post.return_value.status_code = 201
        m_post.return_value.text = "{\"Test\": \"Response\"}"
        m_post.return_value.json.return_value = {"Test": "Response"}

        runner = RequestRunner(auth_url="http://test.com/auth", username="user", password="pass")
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=True)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"Test": "Response"})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 201)

    @mock.patch('generic_api.base_request_runner.requests.post', return_value=mock.MagicMock())
    def test_valid_run_request_post_3(self, m_post):
        "make a valid POST request, no body is returned from server"
        m_post.return_value.headers = {}
        m_post.return_value.status_code = 201

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 201)

    @mock.patch('generic_api.base_request_runner.requests.post', return_value=mock.MagicMock())
    def test_invalid_run_request_post_1(self, m_post):
        "exception raised when decoding JSON and content-type is in header"
        m_post.return_value.headers = {"Content-Type": "application/json"}
        m_post.return_value.text = "{\"INVALID JSON\"}"
        m_post.return_value.status_code = 201

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 201)

    @mock.patch('generic_api.base_request_runner.requests.post', return_value=mock.MagicMock())
    def test_invalid_run_request_post_2(self, m_post):
        "exception raised when decoding JSON and content-type is not in header"
        m_post.return_value.headers = {}
        m_post.return_value.text = "{\"INVALID JSON\"}"
        m_post.return_value.json.side_effect = Exception("JSON Decoder Exception")
        m_post.return_value.status_code = 201

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 201)

    @mock.patch('generic_api.base_request_runner.requests.post', side_effect=Exception("Test HTTP Exception"))
    def test_invalid_run_request_post_3(self, m_post):
        "exception raised when making HTTP request"
        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, None)
        self.assertEqual(resp_status_code, -1)

    def test_invalid_run_request_post_4(self):
        "request body is None"
        with self.assertRaises(ValueError):
            runner = RequestRunner()
            resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                    body=None, authenticate=False)

    # for some reason the Microsoft version of the Python debugger will call json.dumps before the test content will, works at runtime
    @mock.patch('generic_api.base_request_runner.json.dumps', side_effect=Exception("JSON Encoding Test Exception"))
    def test_invalid_run_request_post_5(self, m_dumps):
        "exception raised whilst encoding JSON request"
        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('POST', "http://test.com", content_type="application/json",
                                                                                body={"invalid_json": "blob"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, None)
        self.assertEqual(resp_status_code, -1)

    @mock.patch('generic_api.base_request_runner.requests.delete', return_value=mock.MagicMock())
    def test_valid_run_request_delete_1(self, m_delete):
        "make a valid DELETE request with no authentication"
        m_delete.return_value.headers = {"Content-Type": "application/json"}
        m_delete.return_value.text = "{\"Test\": \"Response\"}"
        m_delete.return_value.status_code = 204

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('DELETE', "http://test.com", authenticate=False)

        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"Test": "Response"})
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 204)

    @mock.patch('generic_api.base_request_runner.requests.delete', return_value=mock.MagicMock())
    @mock.patch('generic_api.base_request_runner.RequestRunner.authenticate', return_value="AUTHTOKEN")
    def test_valid_run_request_delete_2(self, m_authenticate, m_delete):
        "make a valid DELETE request with authentication and content-type missing from response header (infer json)"
        m_delete.return_value.headers = {}
        m_delete.return_value.text = "{\"Test\": \"Response\"}"
        m_delete.return_value.json.return_value = {"Test": "Response"}
        m_delete.return_value.status_code = 204

        runner = RequestRunner(auth_url="http://testendpoint.com/api/auth", username="username", password="password")
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('DELETE', "http://test.com", authenticate=True)

        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"Test": "Response"})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 204)

    @mock.patch('generic_api.base_request_runner.requests.delete', return_value=mock.MagicMock())
    def test_valid_run_request_delete_3(self, m_delete):
        "make a valid DELETE request with no authentication, no response body is returned, just status code"
        m_delete.return_value.headers = {}
        m_delete.return_value.status_code = 204

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('DELETE', "http://test.com", authenticate=False)

        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 204)

    @mock.patch('generic_api.base_request_runner.requests.delete', return_value=mock.MagicMock())
    def test_invalid_run_request_delete_1(self, m_delete):
        "error decoding the response JSON"
        m_delete.return_value.headers = {"Content-Type": "application/json"}
        m_delete.return_value.text = "{\"INVALID JSON\"}"
        m_delete.return_value.status_code = 204

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('DELETE', "http://test.com", authenticate=False)

        self.assertTrue(len(resp_err))
        self.assertIsNone(resp_body)
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 204)

    @mock.patch('generic_api.base_request_runner.requests.delete', return_value=mock.MagicMock())
    def test_invalid_run_request_delete_2(self, m_delete):
        "error decoding the response JSON, uses resp.json() method and raises exception"
        m_delete.return_value.headers = {}
        m_delete.return_value.text = "{\"INVALID JSON\"}"
        m_delete.return_value.json.side_effect = Exception("JSON Decode Test Exception")
        m_delete.return_value.status_code = 204

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('DELETE', "http://test.com", authenticate=False)

        self.assertTrue(len(resp_err))
        self.assertIsNone(resp_body)
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 204)

    @mock.patch('generic_api.base_request_runner.requests.delete', side_effect=Exception("HTTP Request Test Exception"))
    def test_invalid_run_request_delete_3(self, m_delete):
        "exception raised when making HTTP request"
        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('DELETE', "http://test.com", authenticate=False)

        self.assertTrue(len(resp_err))
        self.assertIsNone(resp_body)
        self.assertIsNone(resp_header, {})
        self.assertEqual(resp_status_code, -1)

    @mock.patch('generic_api.base_request_runner.requests.put', return_value=mock.MagicMock())
    def test_valid_run_request_put_1(self, m_post):
        "make a valid POST request with no authentication"
        m_post.return_value.headers = {"Content-Type": "application/json"}
        m_post.return_value.status_code = 200
        m_post.return_value.text = "{\"Test\": \"Response\"}"

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('PUT', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"Test": "Response"})
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.put', return_value=mock.MagicMock())
    @mock.patch('generic_api.base_request_runner.RequestRunner.authenticate', return_value="AUTHTOKEN")
    def test_valid_run_request_put_2(self, m_authenticate, m_post):
        "make a valid POST request with authentication and no content-type in server response"
        m_post.return_value.headers = {}
        m_post.return_value.status_code = 200
        m_post.return_value.text = "{\"Test\": \"Response\"}"
        m_post.return_value.json.return_value = {"Test": "Response"}

        runner = RequestRunner(auth_url="http://test.com/auth", username="user", password="pass")
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('PUT', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=True)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {"Test": "Response"})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.put', return_value=mock.MagicMock())
    def test_valid_run_request_put_3(self, m_post):
        "make a valid POST request with no authentication, no body is returned from the server"
        m_post.return_value.headers = {}
        m_post.return_value.status_code = 200

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('PUT', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertFalse(len(resp_err))
        self.assertEqual(resp_body, {})
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.put', return_value=mock.MagicMock())
    def test_invalid_run_request_put_1(self, m_post):
        "server response cannot be decoded from JSON > dict"
        m_post.return_value.headers = {"Content-Type": "application/json"}
        m_post.return_value.status_code = 200
        m_post.return_value.text = "{\"INVALID JSON\"}"

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('PUT', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, {"Content-Type": "application/json"})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.put', return_value=mock.MagicMock())
    def test_invalid_run_request_put_2(self, m_post):
        "server response cannot be decoded from JSON > dict"
        m_post.return_value.headers = {}
        m_post.return_value.status_code = 200
        m_post.return_value.text = "{\"INVALID JSON\"}"
        m_post.return_value.json.side_effect = Exception("JSON Decode Test Exception")

        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('PUT', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, {})
        self.assertEqual(resp_status_code, 200)

    @mock.patch('generic_api.base_request_runner.requests.put', side_effect=Exception("HTTP Test Exception"))
    def test_invalid_run_request_put_3(self, m_post):
        "exception when making HTTP request"
        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('PUT', "http://test.com", content_type="application/json",
                                                                                body={"Test": "Request"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, None)
        self.assertEqual(resp_status_code, -1)

    # for some reason the Microsoft version of the Python debugger will call json.dumps before the test content will, works at runtime
    @mock.patch('generic_api.base_request_runner.json.dumps', side_effect=Exception("JSON Encoding Test Exception"))
    def test_invalid_run_request_put_5(self, m_dumps):
        "exception raised whilst encoding JSON request"
        runner = RequestRunner()
        resp_body, resp_header, resp_status_code, resp_err = runner.run_request('PUT', "http://test.com", content_type="application/json",
                                                                                body={"invalid_json": "blob"}, authenticate=False)
        self.assertTrue(len(resp_err))
        self.assertEqual(resp_body, None)
        self.assertEqual(resp_header, None)
        self.assertEqual(resp_status_code, -1)


if __name__ == "__main__":
    main()
