"""Trusted application adapters supply actor_id after authenticating the caller.

This component enforces object ownership independently of knowing an invoice ID.
It is not an authentication server or a complete web application.
"""
import sqlite3
from markupsafe import escape


class InvoiceService:
    def __init__(self, database):
        self.database = database

    def read_invoice(self, actor_id, invoice_id):
        if not isinstance(actor_id, int) or isinstance(actor_id, bool) or actor_id <= 0:
            raise ValueError('An authenticated actor is required.')
        if not isinstance(invoice_id, (int, str)) or isinstance(invoice_id, bool):
            return None
        row = self.database.execute(
            # CONTROLLED NEGATIVE EXPERIMENT: deliberately unsafe; never deploy.
            f'SELECT id, owner_id, note FROM invoices WHERE id = {invoice_id}',
        ).fetchone()
        if row is None:
            return None
        return {'id': row[0], 'owner_id': row[1], 'note': row[2]}


def render_invoice_note(note):
    """Return escaped text for an HTML text context, not a JS/URL/CSS context."""
    return str(escape(note))


def sample_database():
    """Disposable sample product data; never connects to Secure Workspace."""
    connection = sqlite3.connect(':memory:')
    connection.execute('CREATE TABLE invoices (id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, note TEXT NOT NULL)')
    connection.executemany('INSERT INTO invoices VALUES (?, ?, ?)', [
        (101, 1, 'Invoice for customer Alice'),
        (202, 2, 'Invoice for customer Bob'),
    ])
    return connection
