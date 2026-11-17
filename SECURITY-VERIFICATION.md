# Product security verification

This repository contains an InvoiceHub data-access/rendering component and actual
security checks. It is separate from the Secure Workspace task-management platform.
The component does not implement browser authentication; its application adapter
must authenticate the caller before supplying the trusted actor ID.

The required workflow is `.github/workflows/security.yml`:

- **Security regression tests:** real SQLite reads verify owner access, refused
  cross-customer access, rejected invalid actors, parameterized query behavior,
  and safe escaping for an HTML text context.
- **Static analysis (Bandit):** reports medium/high issues at medium/high confidence
  in `invoicehub`, not in the fixtures or the CI tools themselves.
- **Dependency audit:** checks the pinned runtime requirements for known published
  vulnerabilities. Tool/network errors fail the job rather than pretending success.

JUnit and JSON reports are retained as workflow artifacts for seven days. Actions
are pinned to full commits, have read-only repository permissions, do not persist
checkout credentials and receive no production secrets. The checked-out code is
the exact PR head SHA. `pull_request_target` is intentionally not used.

Run locally in an isolated virtual environment:

```text
python -m pip install -r requirements-security.txt
python -m pytest -q --junitxml=reports/security-tests.xml
python -m bandit -r invoicehub -ll -ii -f json -o reports/bandit.json
python -m pip_audit --strict --disable-pip --no-deps -r requirements.txt
```

For a real failure, change the invoice query to omit the ownership predicate or
interpolate untrusted identifiers. The access/injection tests should fail because
actual data becomes accessible; Bandit may also identify the unsafe query. Restore
parameter binding and ownership checks to obtain a new passing commit. Branch names
do not determine outcomes. Never deploy the intentionally unsafe branch.

The `security/integration-v2` branch adds this setup for review. The passing and
failing branches can target it while setup is unmerged. After reviewing/merging the
setup, regular product PRs should target `main`.

Passing these selected checks does not prove that the whole product is secure.
Protect workflow/test changes with trusted review and repository branch rules.
Do not automatically mark every manual task-level security requirement Passed.
