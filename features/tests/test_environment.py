from unittest import mock, main, TestCase

from features.environment import populate_template_constants, after_scenario, before_tag


class TestPopulateTemplateConstants(TestCase):
    "test class for the method 'populate_template_constants'"

    def test_valid_1(self):
        "succesfully populate the template constants"
        m_context = mock.MagicMock()

        self.assertTrue(populate_template_constants(m_context))
        self.assertTrue(hasattr(m_context, "templates"))
        self.assertIsInstance(m_context.templates, dict)

    def test_invalid_1(self):
        "given context is invalid"
        with self.assertRaises(RuntimeError):
            populate_template_constants(None)


class TestAfterScenario(TestCase):
    "test class for the method 'after_scenario'"

    def test_valid_1(self):
        "succesfully reset the template/default values, fields already exist"
        m_context = mock.MagicMock()
        m_context.templates = {"test": "data"}
        m_context.default_values = {"test": "data"}

        self.assertIsNone(after_scenario(m_context, mock.MagicMock()))

        self.assertNotIn("test", m_context.templates)
        self.assertNotIn("test", m_context.default_values)

    def test_valid_2(self):
        "succesfully setup the template/default values if they are not already set"
        m_context = mock.MagicMock()

        self.assertIsNone(after_scenario(m_context, mock.MagicMock()))

        self.assertTrue(hasattr(m_context, "templates"))
        self.assertTrue(hasattr(m_context, "default_values"))
        self.assertIsInstance(m_context.templates, dict)
        self.assertIsInstance(m_context.default_values, dict)

    def test_invalid_1(self):
        "invalid context arg given"
        with self.assertRaises(RuntimeError):
            after_scenario(None, None)


class TestBeforeTag(TestCase):
    "test class for the method 'before_tag'"

    @mock.patch("features.environment.use_fixture_by_tag", return_value=None)
    def test_valid_1(self, m_fixture):
        "succesfully detect the need to populate template constants"
        m_context = mock.MagicMock()
        m_tag = mock.MagicMock()
        m_tag.startswith.return_value = True

        self.assertIsNone(before_tag(m_context, m_tag))

    def test_invalid_1(self):
        "invalid args"
        with self.assertRaises(RuntimeError):
            before_tag(None, None)


if __name__ == "__main__":
    main()
