from unittest.mock import Mock, patch
from flask import url_for
from app.views import BaseFormView
from app.forms import BaseForm


class MockFormClass:
    template = "test_form.html"
    title = "Test Form"
    url = "test-form"


class TestBaseFormView:
    def test_init_with_defaults(self):
        view = BaseFormView()
        assert view.form_class == BaseForm
        assert view.template == "form.html"
        assert view.success_endpoint == "main.index"

    def test_init_with_custom_params(self):
        view = BaseFormView(form_class=MockFormClass, template="custom.html", success_endpoint="custom.success")
        assert view.form_class == MockFormClass
        assert view.template == "custom.html"
        assert view.success_endpoint == "custom.success"

    def test_get_form_class(self):
        view = BaseFormView(form_class=MockFormClass)
        assert view.get_form_class() == MockFormClass

    def test_get_template(self):
        view = BaseFormView(template="custom.html")
        assert view.get_template() == "custom.html"

    def test_get_success_url_with_custom_endpoint(self):
        view = BaseFormView(success_endpoint="custom.success")

        with patch("app.views.url_for") as mock_url_for:
            mock_url_for.return_value = "/custom/success"
            result = view.get_success_url()
            mock_url_for.assert_called_once_with("custom.success")
            assert result == "/custom/success"

    def test_get_success_url_with_default(self):
        view = BaseFormView()

        with patch("app.views.url_for") as mock_url_for:
            mock_url_for.return_value = "/main/index"
            result = view.get_success_url()
            mock_url_for.assert_called_once_with("main.index")
            assert result == "/main/index"

    def test_get_context_data_with_title(self):
        view = BaseFormView(form_class=MockFormClass)
        form = Mock()

        context = view.get_context_data(form)

        assert context["form"] == form
        assert context["title"] == "Test Form"

    def test_get_context_data_with_default_title(self):
        class FormWithoutTitle:
            pass

        view = BaseFormView(form_class=FormWithoutTitle)
        form = Mock()

        context = view.get_context_data(form)

        assert context["form"] == form
        assert context["title"] == "Form"

    def test_form_valid(self):
        view = BaseFormView()
        form = Mock()

        with (
            patch("app.views.redirect") as mock_redirect,
            patch.object(view, "get_success_url", return_value="/success"),
        ):
            result = view.form_valid(form)

            view.get_success_url.assert_called_once()
            mock_redirect.assert_called_once_with("/success")
            assert result == mock_redirect.return_value

    def test_form_invalid(self):
        view = BaseFormView()
        form = Mock()
        context = {"form": form, "title": "Test"}

        with (
            patch("app.views.render_template") as mock_render,
            patch.object(view, "get_template", return_value="test.html"),
            patch.object(view, "get_context_data", return_value=context),
        ):
            result = view.form_invalid(form)

            view.get_template.assert_called_once()
            view.get_context_data.assert_called_once_with(form)
            mock_render.assert_called_once_with("test.html", **context)
            assert result == mock_render.return_value

    def test_get_request(self):
        mock_form_class = Mock()
        mock_form = Mock()
        mock_form_class.return_value = mock_form

        view = BaseFormView()
        context = {"form": mock_form, "title": "Test"}

        with (
            patch("app.views.render_template") as mock_render,
            patch.object(view, "get_form_class", return_value=mock_form_class),
            patch.object(view, "get_template", return_value="test.html"),
            patch.object(view, "get_context_data", return_value=context),
        ):
            result = view.get()

            view.get_form_class.assert_called_once()
            mock_form_class.assert_called_once_with()
            view.get_template.assert_called_once()
            view.get_context_data.assert_called_once_with(mock_form)
            mock_render.assert_called_once_with("test.html", **context)
            assert result == mock_render.return_value

    def test_post_request_valid_form(self):
        mock_form_class = Mock()
        mock_form = Mock()
        mock_form.validate_on_submit.return_value = True
        mock_form_class.return_value = mock_form

        view = BaseFormView()

        with (
            patch.object(view, "get_form_class", return_value=mock_form_class),
            patch.object(view, "form_valid", return_value="redirect_response"),
        ):
            result = view.post()

            view.get_form_class.assert_called_once()
            mock_form_class.assert_called_once_with()
            mock_form.validate_on_submit.assert_called_once()
            view.form_valid.assert_called_once_with(mock_form)
            assert result == "redirect_response"

    def test_post_request_invalid_form(self):
        mock_form_class = Mock()
        mock_form = Mock()
        mock_form.validate_on_submit.return_value = False
        mock_form_class.return_value = mock_form

        view = BaseFormView()

        with (
            patch.object(view, "get_form_class", return_value=mock_form_class),
            patch.object(view, "form_invalid", return_value="render_response"),
        ):
            result = view.post()

            view.get_form_class.assert_called_once()
            mock_form_class.assert_called_once_with()
            mock_form.validate_on_submit.assert_called_once()
            view.form_invalid.assert_called_once_with(mock_form)
            assert result == "render_response"


class TestBaseFormViewIntegration:
    def test_view_with_flask_app(self, app):
        with app.app_context():
            view = BaseFormView(form_class=MockFormClass)

            form_class = view.get_form_class()
            assert form_class == MockFormClass

            template = view.get_template()
            assert template == "form.html"

            success_url = view.get_success_url()
            assert success_url == url_for("main.index")

    def test_multiple_view_instances(self):
        view1 = BaseFormView(form_class=MockFormClass, template="form1.html")
        view2 = BaseFormView(template="form2.html", success_endpoint="other.success")

        assert view1.form_class == MockFormClass
        assert view1.template == "form1.html"
        assert view1.success_endpoint == "main.index"

        assert view2.form_class == BaseForm
        assert view2.template == "form2.html"
        assert view2.success_endpoint == "other.success"

    def test_view_inheritance_patterns(self):
        class CustomFormView(BaseFormView):
            form_class = MockFormClass
            template = "custom.html"
            success_endpoint = "custom.success"

        view = CustomFormView()

        assert view.form_class == MockFormClass
        assert view.template == "custom.html"
        assert view.success_endpoint == "custom.success"

        view_with_overrides = CustomFormView(template="override.html", success_endpoint="override.success")

        assert view_with_overrides.form_class == MockFormClass
        assert view_with_overrides.template == "override.html"
        assert view_with_overrides.success_endpoint == "override.success"

    def test_view_methods_called_in_sequence(self):
        view = BaseFormView()
        mock_form = Mock()

        with (
            patch.object(view, "get_form_class") as mock_get_form_class,
            patch.object(view, "get_template") as mock_get_template,
            patch.object(view, "get_context_data") as mock_get_context,
            patch("app.views.render_template") as mock_render,
        ):
            mock_form_class = Mock()
            mock_form_class.return_value = mock_form
            mock_get_form_class.return_value = mock_form_class
            mock_get_template.return_value = "test.html"
            mock_get_context.return_value = {"form": mock_form}

            view.get()

            mock_get_form_class.assert_called_once()
            mock_form_class.assert_called_once()
            mock_get_template.assert_called_once()
            mock_get_context.assert_called_once_with(mock_form)
            mock_render.assert_called_once()

    def test_success_endpoint_flexibility(self):
        view = BaseFormView(success_endpoint="custom.endpoint")

        with patch("app.views.url_for") as mock_url_for:
            mock_url_for.return_value = "/custom/path"
            result = view.get_success_url()

            mock_url_for.assert_called_once_with("custom.endpoint")
            assert result == "/custom/path"
