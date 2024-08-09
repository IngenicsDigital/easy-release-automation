# 1. Getting Started For Developers

## 1.1. Setting Up Project for Development

### 1.1.1. General

1. Execute the setup script (it will setup a venv and install ERA automatically)

    ```bash
        ./scripts/setup-era.sh
    ```

2. Check if you are inside the `.venv` otherwise use `. .venv/bin/activate` for activation

**Attention**: For the following steps you have to be inside the virtual environment!

### 1.1.2. For VS Code

For developing under VS code it is recommended to use the existing configuration file `settings.json`.
The VS code configuration integrates the linting settings into the editor and allows auto-formatting on save.
To do so, VS code requires an not yet existing path to the black module.

Therefore, execute the tox-linting environment once:

1. Execute the linting job

    ```bash
        tox -e lint
    ```

### 1.2. Directory Layout

```bash
    .
    ├── flakehell_baseline.txt      // error baseline for FlakeHell
    ├── MANIFEST.in                 // include files for tox (only required for setup.py)
    ├── pyproject.toml              // PEP 517/518 conform standard:
    |                               // - setup project specifications
    |                               // - configure linting, mypy
    ├── requirements-test.txt       // packages required for testing
    |── tox.ini                     // configure tox
    ├── scripts
    │   └── setup-era.sh            // setup era locally development env with script
    └── doc                         // markdown documentation
```

[comment]: <> (tree /f . -I 'tests|tcucore|conf|doc|artifacts|tcucore.egg-info')

## 1.2. Guideline for Development

### 1.2.1 Testing And Linting

New code contributions should only be committed and merged, when the following three commands run
through successfully:

- Test tox commands lint, mypy, test

```bash
    tox -e lint
    tox -e mypy
    tox -e test
```

If those commands do not have a successful result, the CI-Pipeline will indicate errors.

### 1.2.2 Pin Requirements Using Pip-Compile

After updating python dependencies in the `pyproject.toml`, the requirements.txt and
requirements-test.txt must be regenerated using:

```bash
pip-compile -o requirements.txt pyproject.toml
```

```bash
pip-compile --extra test -o requirements-test.txt pyproject.toml
```

Compiling the `pyproject.toml` requirements pins all dependencies and sub-dependencies, allowing
for reproducible results.

## 1.2. Developing Plugins

You can introduce new plugins to ERA by adding new entry-points in the `pyproject.toml` under the
corresponding groups:

- [project.entry-points."repository.validation"]
- [project.entry-points."repository.modification"]

Example:

```yaml
    [project.entry-points.validation] 
    <validation-plugin-name> = <module.path.to.your.plugin1>:<ValidationPluginClass1>
    [project.entry-points.modification] 
    <modification-plugin-name> = <module.path.to.your.plugin2>:<ModificationPluginClass2>
```

The plugins can then be referenced in the `release-config.yml` for the corresponding steps:

- [project.entry-points.modification] can be used for:
  - `release_modification`-steps
  - `merge_back_finalization`-steps
- [project.entry-points.validation] can be used for
  - `release_validation`-steps

The following yaml-configuration shows an schematic example for the `release-config.yml`:

```yaml
    global_config: 
        ...

    repositories:
        your-repository:
            ...
            plugins:
                release_modification:
                    - <modification-plugin-name>: {kwargs}
                release_validation:
                    - <validation-plugin-name>: {kwargs}
                merge_back_finalization:
                    - <modification-plugin-name>: {kwargs}
```