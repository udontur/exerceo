## Commands
### UV
Initialize the project
```
uv init <PROJECT>
```
### Package Management
adding a package
```
uv add <PKGS>
```
Install & Sync packages to venv
```
uv sync
```
Dependency tree
```
uv tree
```
### Virtual Environment
Initialization
```
uv venv
```
Activate the venv
```
source .venv/bin/activate
```
Deactive the venv
```
deactivate
```
### Nix
Fix Nix dependencies
```
fix-python --venv .venv --libs assets/nix/libs.nix
```
### Syntax
Linter
```
ruff check .
```
Formatter
```
ruff format .
```

