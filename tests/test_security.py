import pytest
from invoicehub.service import InvoiceService, render_invoice_note, sample_database


@pytest.fixture
def service():
    connection = sample_database()
    yield InvoiceService(connection)
    connection.close()


def test_owner_can_read_own_invoice(service):
    assert service.read_invoice(1, 101)['owner_id'] == 1


def test_other_customer_cannot_read_private_invoice(service):
    assert service.read_invoice(2, 101) is None


def test_bob_can_still_read_his_own_invoice(service):
    assert service.read_invoice(2, 202)['owner_id'] == 2


@pytest.mark.parametrize('invoice_id', ['0 OR 1=1', '101 OR owner_id = 2', '101; DROP TABLE invoices; --'])
def test_injection_input_does_not_change_query_semantics(service, invoice_id):
    assert service.read_invoice(2, invoice_id) is None
    assert service.read_invoice(2, 202)['id'] == 202


@pytest.mark.parametrize('actor_id', [None, 0, -1, True, '1 OR 1=1'])
def test_invalid_actor_is_rejected(service, actor_id):
    with pytest.raises(ValueError):
        service.read_invoice(actor_id, 101)


def test_unknown_invoice_does_not_disclose_data(service):
    assert service.read_invoice(1, 999) is None


def test_customer_note_is_escaped_for_html_text():
    rendered = render_invoice_note('<script>alert("fixture")</script>')
    assert '<script>' not in rendered
    assert '&lt;script&gt;' in rendered


def test_plain_note_remains_readable():
    assert render_invoice_note('Invoice paid') == 'Invoice paid'


def test_string_identifier_still_requires_the_correct_owner(service):
    assert service.read_invoice(1, '101')['owner_id'] == 1
    assert service.read_invoice(2, '101') is None


def test_image_markup_is_escaped_as_customer_text():
    rendered = render_invoice_note('<img src=x onerror="alert(1)">')
    assert '<img' not in rendered
    assert '&lt;img' in rendered
