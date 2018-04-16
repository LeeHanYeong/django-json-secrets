# django-json-secrets

**django-json-secrets** is a package that helps you import the secret values managed by JSON file into Django.

## Requirements

- Python (3.6)
- Django (>2.0)

## Before installation

### Split the settings module

When Project name is mysite, initial Django structure:

```
mysite/
	__init__.py
	settings.py
	urls.py
	...
```

---

Split the settings module and move everything to `base.py`

```
mysite/
	settings/
		__init__.py
		base.py
		local.py
	urls.py
```

---

Modify `local.py` so that `local.py` gets all the contents of `base.py`.

**`mysite/settings/local.py`**

```python
from .base import *
```
---

Modify `mysite/settings/__init__.py` to use `mysite.settings.local` as default

**`mysite/settings/__init__.py`**

```python
import os

SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
if not SETTINGS_MODULE or SETTINGS_MODULE == 'mysite.settings':
    from .local import *
```


## Installation

Install using `pip`

```
pip install django-json-secrets
```

Define `SECRETS_DIR`

```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRETS_DIR = os.path.join(BASE_DIR, '.secrets')
```

After defining `SECRETS_DIR`, import and execute function `import_secrets`

```python
from djs import import_secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRETS_DIR = os.path.join(BASE_DIR, '.secrets')
import_secrets()
```

## (Optional) Using `SECRETS_MODULES`

**django-json-secrets** evaluates the value defined in JSON using Python's `eval()` function.

If you need a specific Python module in the `eval()` process, you need to add the module name and module's full path string(or Python module object) to `SECRETS_MODULES` dictionary.

```python
# If need raven and requests module
import requests

SECRETS_MODULES = {
    # Module's full path string
    'raven': 'raven',
    # Python module object
    'requests': requests,
}
```

JSON values that require `eval()` using the `raven` module example:

```json
"RAVEN_CONFIG": {
	"release": "raven.fetch_git_sha(os.path.abspath(os.pardir))"
}
```


## Example usage

Specify the folder that contains the JSON secret files, and name the JSON file as the module name to assign the value to.

If the folder where the JSON secret files are gathered is `.secrets` and the `settings` module is packaged, it has the following structure.

```
# settings module
settings/
	__init__.py
	base.py
	local.py

# Secrets DIR
.secrets/
	base.json
	local.json
```

### Secret JSON files

**`.secrets/base.json`**

```json
{
  "SECRET_KEY": "SDFSEFSDFDF"
}
```

**`.secrets/local.json`**

```json
{
  "ALLOWED_HOSTS": [
    ".localhost",
    "127.0.0.1",
    ".lhy.kr"
  ]
}
```

### `settings` package's modules

**`settings/base.py`**

```python
from djs import import_secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRETS_DIR = os.path.join(BASE_DIR, '.secrets')
import_secrets()
```

**`settings/local.py`**

```python
from .base import *

import_secrets()
```

### Display secrets

When the `settings` module is loaded, the set secret values are output to the console.

```
- JSON Secrets (base)
 SECRET_KEY = ls@************************************

- JSON Secrets (local)
 ALLOWED_HOSTS
  .localhost
  127.0.0.1
  .lhy.kr
```
