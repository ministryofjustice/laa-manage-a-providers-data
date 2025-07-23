from unittest.mock import Mock, patch

from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField

from app.utils import register_form_view
from app.views import BaseFormView


class MockForm(FlaskForm):
    url = "test-form"
    name = StringField("Name")


class MockCustomView(BaseFormView):
    pass


class TestRegisterFormView:
    def test_register_with_default_blueprint_and_view(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.utils.BaseFormView", mock_view_class), patch("app.main.bp", mock_blueprint):
            register_form_view(MockForm, login_required=False)

        mock_blueprint.add_url_rule.assert_called_once_with(
            "/test-form", view_func="mock_view_func", methods=["GET", "POST"]
        )
        mock_view_class.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_with_custom_blueprint(self):
        custom_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.utils.BaseFormView", mock_view_class):
            register_form_view(MockForm, blueprint=custom_blueprint, login_required=False)

            custom_blueprint.add_url_rule.assert_called_once_with(
                "/test-form", view_func="mock_view_func", methods=["GET", "POST"]
            )
            mock_view_class.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_with_custom_view_class(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_custom_view = Mock()
        mock_custom_view.as_view.return_value = "custom_view_func"

        with patch("app.main.bp", mock_blueprint):
            register_form_view(MockForm, view_class=mock_custom_view, login_required=False)

            mock_blueprint.add_url_rule.assert_called_once_with(
                "/test-form", view_func="custom_view_func", methods=["GET", "POST"]
            )
            mock_custom_view.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_with_all_custom_parameters(self):
        custom_blueprint = Mock(spec=Blueprint)
        mock_custom_view = Mock()
        mock_custom_view.as_view.return_value = "custom_view_func"

        register_form_view(MockForm, view_class=mock_custom_view, blueprint=custom_blueprint, login_required=False)

        custom_blueprint.add_url_rule.assert_called_once_with(
            "/test-form", view_func="custom_view_func", methods=["GET", "POST"]
        )
        mock_custom_view.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_url_generation_from_form_class(self):
        class CustomUrlForm(FlaskForm):
            url = "custom-url-path"

        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.BaseFormView", mock_view_class):
            register_form_view(CustomUrlForm, login_required=False)

            mock_blueprint.add_url_rule.assert_called_once_with(
                "/custom-url-path", view_func="mock_view_func", methods=["GET", "POST"]
            )

    def test_view_name_generation_from_form_class(self):
        class VeryLongFormClassName(FlaskForm):
            url = "test"

        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.BaseFormView", mock_view_class):
            register_form_view(VeryLongFormClassName, login_required=False)

            mock_view_class.as_view.assert_called_once_with("test", form_class=VeryLongFormClassName)

    def test_methods_are_always_get_and_post(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.BaseFormView", mock_view_class):
            register_form_view(MockForm, login_required=False)

            call_args = mock_blueprint.add_url_rule.call_args
            assert call_args[1]["methods"] == ["GET", "POST"]

    def test_form_class_passed_to_as_view(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.BaseFormView", mock_view_class):
            register_form_view(MockForm, login_required=False)

            call_args = mock_view_class.as_view.call_args
            assert call_args[1]["form_class"] == MockForm

    def test_function_returns_none(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.BaseFormView", mock_view_class):
            result = register_form_view(MockForm, login_required=False)

            assert result is None


class TestRegisterFormViewIntegration:
    def test_register_with_real_blueprint(self):
        real_blueprint = Blueprint("test", __name__)
        mock_view_class = Mock()
        mock_view_func = Mock()
        mock_view_class.as_view.return_value = mock_view_func

        register_form_view(MockForm, view_class=mock_view_class, blueprint=real_blueprint, login_required=False)

        # Verify the view class was called correctly
        mock_view_class.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_multiple_forms_same_blueprint(self):
        class Form1(FlaskForm):
            url = "form1"

        class Form2(FlaskForm):
            url = "form2"

        real_blueprint = Blueprint("test", __name__)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = Mock()

        register_form_view(Form1, view_class=mock_view_class, blueprint=real_blueprint, login_required=False)
        register_form_view(Form2, view_class=mock_view_class, blueprint=real_blueprint, login_required=False)

        # Both forms should be registered
        assert mock_view_class.as_view.call_count == 2

        # Check the calls were made with correct form classes
        calls = mock_view_class.as_view.call_args_list
        assert calls[0][1]["form_class"] == Form1
        assert calls[1][1]["form_class"] == Form2

    def test_register_form_with_special_characters_in_name(self):
        class FormWithNumbers123(FlaskForm):
            url = "special-form"

        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.utils.BaseFormView", mock_view_class):
            register_form_view(FormWithNumbers123, blueprint=mock_blueprint, login_required=False)

            mock_view_class.as_view.assert_called_once_with("special_form", form_class=FormWithNumbers123)

    def test_parameter_types_are_correct(self):
        # Test that the function accepts the expected parameter types
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        # This should not raise any type errors if the function signature is correct
        register_form_view(form_class=MockForm, view_class=mock_view_class, blueprint=mock_blueprint, login_required=False)

        # Verify it was called
        mock_blueprint.add_url_rule.assert_called_once()
        mock_view_class.as_view.assert_called_once()
