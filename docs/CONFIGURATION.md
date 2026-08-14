# Configuration

`autofcholv` loads configuration into a typed `Config` object:

1. **Config file** - a JSON or YAML file passed explicitly via the API (`load_config(path)`) or CLI (`--config`). `.env` files are not supported.
2. **Default config file** - `config.default.json` (searched in the current working directory, then packaged library defaults) is loaded automatically if no config file is specified.
3. **Built-in defaults** - fallback defaults from the `Config` dataclass are applied if no config file is found.

YAML supports arrays, so list-style configuration can be written naturally:

```yaml
MULTI_RSI:
  - 14
  - 50
  - 42
```
