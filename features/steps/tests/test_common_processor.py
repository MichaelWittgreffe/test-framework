from unittest import main, mock, TestCase

from behave.runner import Context

from features.steps.common_processor import populate_default_values


class TestPopulateDefaultValues(TestCase):
    "test class for the method 'populate_default_values'"

    def test_valid_1(self):
        "succesfully populate given default values in the context"
        m_context = Context(mock.MagicMock())
        m_context.table = [{"label": "test", "values": 1234}]

        self.assertIsNone(populate_default_values(m_context))

        self.assertTrue(hasattr(m_context, "default_values"))
        self.assertIn("test", m_context.default_values)
        self.assertEqual(m_context.default_values["test"], 1234)

    def test_valid_2(self):
        "no table set for context, should just ignore setting any default value fields"
        m_context = Context(mock.MagicMock())

        self.assertIsNone(populate_default_values(m_context))

        self.assertTrue(hasattr(m_context, "default_values"))
        self.assertEqual(len(m_context.default_values), 0)

    def test_invalid_1(self):
        "context is None"
        with self.assertRaises(RuntimeError):
            populate_default_values(None)


if __name__ == "__main__":
    main()
