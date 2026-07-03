# Configuration

`autofcholv` resolves configuration in the following order (first match wins):

1. **Environment variables** - all required keys must be present in the environment.
2. **Config file** - a JSON or YAML file passed explicitly via the API (`load_config(path)`).
3. **Built-in defaults** - sensible defaults are applied automatically if neither of the above is available.
