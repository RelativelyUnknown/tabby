# Audit classes: identity, access, defaults and configuration

Every hit needs the trace from attacker-controlled input or a reachable deployment state to the decision it affects.

## Identity and access

Every hit needs the trace from attacker-controlled input to the decision ([process-and-reporting.md](process-and-reporting.md)). Fixes are in `tabby/development/code/input-and-secrets-security.md` and `tabby/development/application/apis/shared/api-security-owasp.md`.

### Authorization (the commonest serious bug)

First learn how this project enforces access: decorators, middleware, base classes, DRF `permission_classes`, custom managers and `get_queryset()`, and which field owns a row (`owner_id`, `organization_id`). Then ask for each endpoint that handles user data: **if I am user A and know the ID of user B's object, can I read, change or delete it?** Trace it: where the ID enters (path, query, body), where the object is fetched, and what stands between (the query's own scope, an object-level check, a parent class, middleware, a URL-level decorator). A check anywhere on the path counts; a check on one path does not cover another.

- **Gap indicators:** `get_queryset()` returns `.all()`; `Model.objects.get(pk=pk)` or `session.get(Model, id)` with no owner or tenant in the query; a permission class that checks login but not ownership (`IsAuthenticated` is not ownership; DRF's default permission is `AllowAny` unless settings change it); no `has_object_permission` and an unscoped queryset; an ID from the request body for a sensitive operation.
- **Compare siblings:** the delete route lacks the decorator its list route has; the new route skips what the others do. Admin and internal routes need their own check, and so does every other way to reach the data: background jobs, CLI commands, GraphQL, websockets, export endpoints.
- **Permission matching:** `"admin" in user.role` matches `readonly_admin_viewer`; `any(...)` where `all(...)` was meant; roles kept as comma-separated strings. Compare against an `Enum` or `frozenset`.
- **Mass assignment:** a `for k, v in data.items(): setattr(obj, k, v)` loop is the same bug; `Model(**request.json)`, `update(request.data)`, `serializer.save(**request.data)`, a serializer with `fields = "__all__"`, a pydantic model that accepts `is_admin`, `role` or `owner_id`.
- **Field level:** a response built from the whole ORM object, `__dict__` or `to_dict()` (leaks `password_hash`, internal IDs); fields that only an admin or the owner may see.
- **Not a finding:** hidden or missing authorization in client-side code (the server decides); a path that needs a login the attacker can obtain freely is still a finding.

### Authentication and sessions

- **Enumeration:** identical messages for unknown user and wrong password, and for reset and sign-up ("if that address exists we sent a link"). Timing counts too: when the user is missing, hash a dummy password.
- **One-time codes:** an expiry that `0` or a negative number disables, no cap on attempts (a six-digit code has 1,000,000 values), a code valid until the next is issued, a reset token that is never invalidated. A token is single use only if it is marked used atomically (`UPDATE ... WHERE used = false`), not by read-then-write.
- **Sessions:** a session ID taken from the request (`request.cookies.get("session") or new_id()`) is fixation; a new ID at login and when privileges change (fixation); IDs from `secrets` (never `user_id + time`); `Secure`, `HttpOnly`, `SameSite`; idle and absolute expiry; server-side invalidation on logout; tokens never in URLs.
- **Re-authenticate** before changing the password, e-mail address or MFA, deleting an account or moving money. An e-mail change notifies the old address and confirms the new one.
- **JWT:** the header must not choose the algorithm. `algorithms=[...]` pinned (PyJWT 2 refuses `decode` without it, and an `alg: none` token is rejected when the list is pinned); an RSA public key accepted as an HMAC secret is the RS256-to-HS256 confusion, `exp`, `aud` and `iss` checked, a long random key, no personal data in claims.
- **Webhook receivers:** verify the signature over the raw body, in constant time, with a timestamp window against replay.

### CSRF, CORS, websockets, GraphQL

- **CSRF:** a cookie-authenticated state-changing endpoint needs a token or an Origin check (Django has it by default, Flask needs `CSRFProtect`, FastAPI has none). `@csrf_exempt` on such a view and any state change on `GET` are findings.
- **CORS:** the real holes are a reflected `Origin` with credentials and `Access-Control-Allow-Origin: null` (`*` with credentials is rejected by browsers).

### Business logic

- **Races:** check-then-write on money, stock, coupons and balances without one transaction and a lock or an atomic conditional `UPDATE`. A `threading.Lock` protects one process only; locks in a fixed order avoid deadlock. Test with two concurrent requests.
- **Idempotency keys** must be claimed by a unique insert; look-up-then-create lets two identical requests both run.
- **Workflow:** later steps callable without the earlier ones. See [state-machines.md](../state-machines.md).

## Defaults, configuration and exposure

Every hit needs the trace from attacker-controlled input or a reachable deployment state to the decision it affects ([process-and-reporting.md](process-and-reporting.md)). Settings, environment variables and the project's own constants are server-controlled: they are not a path, URL or command source on their own, but what they default to is the question here. Fixes are in `tabby/development/code/input-and-secrets-security.md`.

### Fail-open defaults

A missing or broken setting must stop the process or fall to the strict behaviour. Two kinds of candidate, judged differently:

- **Configurable:** a lookup with a fallback. It is a bug only if the application actually runs with the fallback. `os.environ.get("SECRET_KEY", "dev")` runs; `os.environ["SECRET_KEY"]` stops with a `KeyError`, which is fail-secure. Before filing it, check how the deployment supplies the variable (Dockerfile `ENV`, compose, Kubernetes manifests, CI, a `.env.example`): every manifest that sets it lowers the severity, none that does is the worst case, and an unclear answer counts as reachable.
- **Unconditional:** insecure as written, with no setting involved: a hardcoded signing key, `bootstrap_admin()` that seeds `admin`/`admin123`, a bucket created `public-read`, `0o666` on a key file. About half of real findings are this kind, and a missing environment variable is no reason to refute one.

A candidate becomes a finding when each step holds: the file is reachable in production; the insecure value is the one that runs; the value is actually insecure; it reaches a security decision (name the sink); and for a configurable one, deployment does not always supply it. An incomplete trace means refuted. By category:

- **Fallback secrets:** a default that feeds signing, encryption, sessions or tokens (`getenv("TOKEN") or "changeme"`, `SECRET_KEY = "dev-secret"`). Not: values generated at random on each boot, cache keys, correlation ids.
- **Default credentials:** a login a running deployment can use, including accounts seeded on first boot and connection strings with a password in a fallback (`docker-compose.yml`, Kubernetes secrets, where base64 `YWRtaW4=` is `admin`). Not: accounts created disabled or with a forced reset, credentials in a README or test fixture ("a credential in prose is one nobody can use; one in `bootstrap_admin()` is a login").
- **Fail-open switches:** read the default, not the flag name: `REQUIRE_AUTH` defaulting to `"false"` requires nothing; an `except Exception: return True` or `pass` around a permission check; an `authenticate()` that returns `None` on error while the caller treats `None` as success. Not: switches whose unconfigured value is the secure one, or flags that are never consulted where the control is enforced.
- **Weak cryptography:** the algorithm alone is never the finding; trace to the use. `hashlib.md5` over a cache key is fine, over a password is not. See [injection-files-crypto.md](injection-files-crypto.md).
- **Permissive access:** ask who gains access, not how wide the value looks: `0o644` on a CDN asset is right, `0o666` on a key file is not; `os.umask(0)`; CORS `*` with credentials; a public bucket. Not: a deliberate public endpoint with a stated reason.
- **Debug and diagnostics:** needs both halves, on by default and a path to a reader who should not see it: `app.run(debug=True)` (the Werkzeug debugger runs code), Django `DEBUG = True`, `ALLOWED_HOSTS = ["*"]`, a traceback or `str(e)` in a response, `/debug`, `/env`, `/config`, `/metrics`, `.git` or `.env` reachable, directory listing (`python -m http.server` is not a production server). A verbose log written to a file only an operator reads is neither.
- **Exposure:** responses with more fields than the caller may see; sensitive responses without `Cache-Control: no-store`; passwords, tokens or whole request bodies in logs.

Find the project's own configuration wrappers first (`get_setting("X", "default")`, a `Settings` class with defaults): a codebase that reads everything through one barely matches generic patterns. Say which patterns you searched. A search that matches nothing looks the same as a clean result, and in `grep -E` use `[[:space:]]` and `[0-9]` rather than `\s` and `\d`, which some builds silently ignore.

### Security parameters and silent failure (API and configuration review)

When reviewing a library's API or a configuration schema, put yourself in three seats: the **attacker** who controls a value, the **lazy developer** who copies the first example, and the **confused developer** who swaps two arguments. For every security-relevant choice ask: what happens with zero, empty, `None`, negative, a value of the wrong type, and an error?

- **Zero, empty, None, negative.** A lifetime or timeout of `0` that means "accept everything" or "never expires"; a negative timeout that makes `now - created > timeout` never true; `max_attempts=0` or `-1` meaning unlimited; `if not key: return True` (no key means skip the check); `stored == ""` equal to an empty submitted password (`"" == ""` is true, and so is `hmac.compare_digest(b"", b"")`). Reject them: a security number must be positive and have both a minimum and a maximum; an empty secret must be refused.
- **Switches.** A boolean that disables a control (`verify_ssl`, `require_auth`) is a cliff; double negatives (`disable_auth: false`) invite mistakes. Config parsers surprise: PyYAML's `safe_load` turns `no`, `NO`, `off` into `False` (the "Norway" problem), a typo such as `fasle` becomes the truthy string `"fasle"`, and `bool("false")` is `True`. Validate the type, reject unknown keys, and reject contradictory pairs (`require_auth: true` with `allow_anonymous: true`). State the precedence when a file, an environment variable and a flag can all set one value.
- **Defaults are not validation.** A secure default protects only callers who omit the argument. A constructor or settings class takes `algorithm`, `mode`, `cipher`, a lifetime, a hostname or a URL from the caller: validate them against an allowlist and a range at construction, so an insecure value is refused when it is created, not when it is used.
- **The caller picks the mechanism.** Any parameter that selects a security mechanism and can come from input (`alg` in a JWT header, a cipher or hash name) lets an attacker downgrade it. Fix the algorithm in code.
- **Silent failure.** A verify function that returns `False` while a caller discards the result; one library raises on failure and another returns a bool, and developers mix them up; `except` blocks that log and carry on as if authentication succeeded; a parse error replaced by a default.

### Frameworks, containers, limits

- **Dockerfile, compose, manifests:** no `USER`; `:latest`; secrets in `ARG`, `ENV` or `COPY .env` (visible in `docker history`); no `.dockerignore` for `.env`, keys and `.git`; `--privileged`, a mounted `/var/run/docker.sock`, `-v /:/host`.
- **Limits:** unbounded bodies, uploads, decompression or a nested-quantifier regex are findings only where a small input from a low-trust caller causes large amplification; otherwise a hardening note, like missing rate limits and security headers.
