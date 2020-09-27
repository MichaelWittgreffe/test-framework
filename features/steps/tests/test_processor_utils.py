from unittest import mock, main, TestCase

from features.steps.processor_utils import get_dot_path_data, get_current_time_ms


class TestGetDotPathData(TestCase):
    "test class for the method 'test_dot_path_data'"

    def test_valid_1(self):
        "succsfully return the data at a json dot path"
        in_data = {
            "foo": {
                "bar": [
                    {
                        "foobar": 1234,
                    }
                ]
            }
        }

        result = get_dot_path_data(in_data, "foo.bar.0.foobar", "json")

        self.assertEqual(result, 1234)

    def test_invalid_1(self):
        "attempt to access an array index that does not exist"
        in_data = {
            "foo": {
                "bar": []
            }
        }

        with self.assertRaises(ValueError):
            get_dot_path_data(in_data, "foo.bar.25", "json")

    def test_invalid_2(self):
        "attempt to access a key item that des not exist"
        in_data = {
            "foo": {}
        }

        with self.assertRaises(ValueError):
            get_dot_path_data(in_data, "foo.bar", "json")

    def test_invalid_3(self):
        "invalid data_type arg given"
        with self.assertRaises(TypeError):
            get_dot_path_data({}, "foo.bar", "unsupported data type")


class TestGetCurrentTimeMs(TestCase):
    "test class for the method 'get_current_time_ms'"

    @mock.patch("features.steps.processor_utils.time.time", return_value=5)
    def test_valid_1(self, m_time):
        "succesfully get the time in ms"
        self.assertEqual(get_current_time_ms(), 5000)


if __name__ == "__main__":
    main()
