Release type: minor

- Check if the environment really changed. Before a reformatting the YAML file would cause a rewrite and the `pre-commit` hook to fail.
- Do not use mamba when exporting as it adds some spurious dependencies.
- Refactor logging a bit.
- Package now gets tested automatically on MacOS.
