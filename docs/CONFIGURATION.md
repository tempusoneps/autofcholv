# Configuration

`autofcholv` loads configuration into a typed `Config` object:

1. **Config file** - a JSON or YAML file passed explicitly via the API (`load_config(path)`). `.env` files are not supported.
2. **Built-in defaults** - sensible defaults are applied automatically if no config file is provided.

YAML supports arrays, so list-style configuration can be written naturally:

```yaml
MULTI_RSI:
  - 14
  - 50
  - 42
```
