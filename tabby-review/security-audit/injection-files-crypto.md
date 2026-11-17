# Audit classes: injection, files, network and cryptography

For each class: where to look, what makes a hit a finding, what refutes it. Every hit needs the trace from attacker-controlled input to the sink. Fixes are the write-time rules in `tabby/development/code/input-and-secrets-security.md`.

## Injection, execution and output

For each class: where to look, what makes a hit a finding, what refutes it. Every hit still needs the trace from attacker-controlled input to the sink ([process-and-reporting.md](process-and-reporting.md)). Fixes are the write-time rules in `tabby/development/code/input-and-secrets-security.md`.

### SQL and query languages

- **Look:** `execute`, `executemany`, `text()`, `.raw()`, `.extra()`, `RawSQL`, `cursor.execute` given an f-string, `%`, `.format` or `+`; table, column or `ORDER BY` taken from input; `filter(**request.GET)` or `Model.objects.filter(**data)`, which lets the caller choose fields and lookups.
- **Finding:** the value is attacker-controlled and is not bound. An identifier cannot be bound, so it needs an allowlist.
- **Refuted by:** bound parameters, ORM keyword filters with fixed names, constants.
- **NoSQL:** a JSON body used directly as a filter lets the caller send operators (`{"password": {"$gt": ""}}`); `$where` runs code. Coerce to `str` or parse into a typed model.

### OS commands

- **Look:** `shell=True`, `os.system`, `os.popen`, `subprocess` with a string; an argument list that still carries a value starting with `-` (argument injection into `git`, `tar`, `curl`; needs `--`).
- **Finding:** attacker-controlled data reaches the command line. `shlex.quote` is for building a shell string, not a replacement for a list. If a library call does the job (`os.makedirs`, `shutil`), the subprocess is the smell.
- **Refuted by:** a fixed argument list, an allowlist of command names, constants.

### Templates and output (XSS)

- **Look:** `render_template_string`, `Template(user_text)`, `Environment().from_string(user_text)`; `|safe`, `Markup`, `mark_safe`, `format_html` given unescaped text, `{% autoescape off %}`, `jinja2.Environment()` rendering HTML (autoescape is off by default), HTML built with f-strings, user text in `<script>`, `href` or `src` (`javascript:` URLs), uploads of HTML or SVG served inline.
- **Finding (template injection):** user text is the template. To confirm in a scratch test, `{{7*7}}` renders `49`.
- **Finding (XSS):** an escape hatch applied to user data. Automatic escaping by Django, Flask or Jinja with `select_autoescape()` is a control; only its escape hatches are findings.

### Execution and deserialization

- **Look:** `eval`, `exec`, `compile`, `__import__`, `importlib.import_module` or `getattr(module, name)()` on input. `pickle`, `marshal`, `shelve`, `dill`, `jsonpickle`, `joblib.load`, `pandas.read_pickle`, `numpy.load(allow_pickle=True)`, a `torch.load` of an untrusted file. `yaml.load` with `Loader` or `UnsafeLoader` (PyYAML 6 requires a loader argument, and those two ran a `!!python/object/apply` payload; `SafeLoader` and `FullLoader` blocked it).
- **Finding:** the data crosses a trust boundary: an uploaded model, a cache or queue another party can write, a user's file, a cookie. Signing the data with a server-held key (`hmac.compare_digest` on the digest) is a mitigation, not a reason to keep pickle.
- **Refuted by:** a trusted-only source (the project's own build output); JSON or a typed model.

### XML

- **Look:** `xml.etree`, `minidom`, `sax`, `lxml` parsing outside data.
- **Finding:** the standard-library parsers expand internal entities (a small document can grow large). `lxml` 6.1.3 did not resolve an external entity with default settings (`Entity 'xxe' not defined`) and read `file:///etc/hostname` with `resolve_entities=True`; so the finding is `resolve_entities=True`, `load_dtd=True`, or an old `lxml`, not the default. `defusedxml` is the fix for untrusted XML.

### Type confusion and AI features

- **Type confusion:** type hints and casts do not validate. `request.json()["id"]` can be a list, dict, float or string; a handler that uses it as an ID, a limit or a filter value without parsing behaves unpredictably. A finding only when the wrong type reaches a security decision (a check that passes on a list, an operator injected into a query).
- **LLM features:** user-controlled text in a prompt is not a vulnerability by itself. It becomes one when the model also holds tools, files or credentials, or its output reaches `eval`, a shell, SQL or a path unchecked. Delimiters and "ignore previous instructions" filters are not controls; what the model's output is allowed to do is.

## Files, network and cryptography

Every hit needs the trace from attacker-controlled input to the sink ([process-and-reporting.md](process-and-reporting.md)). Settings, environment variables and the project's own constants are server-controlled: they are not a path, URL or command source unless a secret is committed or the value is built from user input. Fixes are in `tabby/development/code/input-and-secrets-security.md`.

### Paths, uploads, archives

- **Paths:** `open(os.path.join(base, user))` (an absolute `user` replaces `base`; `..` climbs out), `send_file(user_path)`, `Path(user).read_text()`, `shutil.copy(user_src, user_dst)`. A string `startswith(base)` check is itself a finding: `/app/files_evil` passes for `/app/files`. The check that holds is resolving, then `is_relative_to`. Symlinks inside an upload or archive defeat a name check.
- **Uploads:** the name, size, type and content are all attacker-controlled. Look for a client filename used as a path, a type taken from the header or extension, storage under the web root, HTML or SVG served inline (script runs on your origin), no size cap.
- **Archives:** `tarfile.extractall` without `filter="data"` (the default filter arrives in 3.14; 3.13 warns); `zipfile.extractall` or a hand-written loop without a per-member path check; no cap on total size or file count. `zipfile` stops reading at a member's declared size, so summing `infolist()` sizes is a valid pre-check in CPython (checked with a forged header).

### Server-side requests (SSRF)

- **Look:** a URL from the request fetched by `requests`, `httpx`, `urllib`, `aiohttp`, a webhook sender, an image or link-preview proxy, a PDF renderer.
- **Finding:** the caller controls the **host or scheme**. Controlling only the path of a fixed host is not SSRF. The impact is what the server can reach that the caller cannot: internal services that trust localhost, the cloud metadata service (`169.254.169.254`, `169.254.170.2`, `metadata.google.internal`), `file://` or other schemes.
- **A check is weak when** it inspects the URL string. The OS resolver turns `2130706433`, `0x7f000001`, `0177.0.0.1` and `127.1` into `127.0.0.1` (all four checked), while `ipaddress.ip_address` rejects them; `::ffff:127.0.0.1` is the same host in IPv6 form. It is also weak when it validates, then lets the HTTP library resolve again (rebinding), or follows redirects (`allow_redirects=False` and revalidate each hop).
- **A check holds when** it resolves with `getaddrinfo`, requires `ip.is_global` for every returned address (private, loopback, link-local, IPv4-mapped and carrier-grade NAT `100.64.0.0/10` are all `is_global == False`), and connects to that address. Rewriting the URL to the IP and sending a `Host` header breaks TLS verification (`SSLError`, checked); keep the hostname and force the connection address instead.

### Cryptography and secrets

- `random` for tokens or keys (use `secrets`); `uuid.uuid1()` as an unguessable ID (it carries a timestamp and a node ID; `uuid4` is random); MD5 or SHA-1 for anything security-related (checksums and cache keys are fine).
- Encryption: use the `cryptography` package's `AESGCM`, `ChaCha20Poly1305` or `Fernet`. Findings: ECB mode, CBC without a MAC (padding oracle), a fixed or counter nonce that is not persisted, a nonce reused with the same key, a key built from a short password without a KDF, home-made schemes.
- TLS: `verify=False`, `ssl._create_unverified_context`, `check_hostname = False`, `urllib3.disable_warnings()`. Use `ssl.create_default_context()` and leave the cipher list alone.
- Key and secret handling (Python cannot wipe an immutable `str` or `bytes`; a `bytearray` can be overwritten, and the honest control is a short lifetime and no copies into logs, errors or exceptions' `repr`): committed `.env` and keys, secrets in logs, URLs, error pages, container images or a settings object's `repr`; one key for every purpose; no way to rotate (tag ciphertext with a key version).
- Timing: `==`, `startswith` or `in` on tokens, MACs or password hashes (use `hmac.compare_digest`; `secrets.compare_digest` is the same function). Give it `bytes`: two `str` that contain a non-ASCII character raise `TypeError` (checked), which a login handler turns into a 500 or, worse, a skipped check. Python's `int`, `//`, `%` and `pow` are not written to be constant-time, so a key-dependent computation in pure Python (a hand-written RSA, a modular reduction of a secret) is a finding; use a library built for it.
- A hash is not a key-derivation function (`sha256(password)` as a key is fast to brute force; use `hashlib.scrypt`, PBKDF2 or Argon2), and encryption is not password storage (one stolen master key exposes every password; store a salted one-way hash).
- Decryption that tells the caller *why* it failed ("invalid padding" against "MAC mismatch") is a padding oracle; fail with one error, and prefer authenticated encryption.
