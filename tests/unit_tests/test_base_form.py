from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired

from app.forms import BaseForm


class TestForm(BaseForm):
    name = StringField(validators=[InputRequired()])
    age = IntegerField(validators=[InputRequired()])
    referrer = StringField()


def test_base_form_has_changed_default(app):
    form = TestForm(name="test", age=10)
    assert form.has_changed() is False


def test_base_form_has_changed_submit_exact(app):
    """Submit the same data as the initiation data"""
    with app.test_request_context(method="POST", data={"name": "test", "age": "10"}):
        form = TestForm(name="test", age=10)
        assert form.has_changed() is False


def test_base_form_has_changed_one_change(app):
    """Submit a single change"""
    with app.test_request_context(method="POST", data={"name": "test", "age": "10", "referrer": "test"}):
        form = TestForm(name="test", age=10)
        assert form.has_changed() is True


def test_base_form_has_changed_all_changed(app):
    """Submit a change to all fields"""
    with app.test_request_context(method="POST", data={"name": "test2", "age": "11", "referrer": "test"}):
        form = TestForm(name="test", age=10)
        assert form.has_changed() is True


def test_base_form_has_changed_no_init_data(app):
    """Submit test data and do not pass initial data to form instantiation"""
    with app.test_request_context(method="POST", data={"name": "test", "age": "10"}):
        form = TestForm()
        assert form.has_changed() is True
