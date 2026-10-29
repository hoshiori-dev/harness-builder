<file>:<line>: <what is wrong, naming the offending symbol or import>.
  Rule: <the rule in one line> (<knowledge file that states it>).
  Instead: <the allowed alternative, with a path or example to copy>.

app/billing/service.py:12: imports infra.db, which is inside infra/.
  Rule: app/ must not import from infra/ (.agents/knowledge/architecture.md).
  Instead: depend on the interface in app/ports/ and let infra/ implement it; see app/ports/repository.py.

ERROR app/billing/service.py: cannot read: Permission denied.
  Fix: make the file readable or remove it from the input; the check did not pass.
