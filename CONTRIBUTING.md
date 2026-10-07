# Contributing to AIVE

Start with the [setup guide](docs/getting-started.md) and [architecture overview](docs/architecture.md).

## Report a problem or suggest a feature

[Open an issue](https://github.com/desanv01/ai-video-editor/issues) with the workflow, expected result, actual result, and reproduction steps. Include the application mode, source commit, and relevant provider/runtime information.

Use synthetic or permission-cleared examples. Remove credentials, private transcripts, course content, and personal information from logs and screenshots before sharing them. Describe suspected security problems without posting secrets or exploit details in public.

## Submit a change

1. Create a branch from `main`.
2. Keep the change focused and preserve lecturer approval and manual-override behavior.
3. Run checks appropriate to the files and workflow you changed.
4. Open a pull request describing the problem, resulting behavior, validation, and limitations.

Documentation-only changes should check relative links, assets, commands, and feature claims. Runtime changes should include meaningful validation of the affected workflow.

## Development checks

Run these from the repository root using a configured development environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -p test_*.py -v
npm run build --prefix desktop
docker compose config --quiet
```

For Tauri changes, run `cargo check` from `desktop/src-tauri/` with Rust and the Windows C++ build tools installed. Packaged-desktop Compose validation additionally needs the launcher-provided storage variables.

Use synthetic fixtures for tests; disclose live provider use and cost before running those checks. State what each check actually verified.

Historical results are recorded in [the verification report](docs/reproducibility/VERIFICATION_RESULTS.md). They do not establish the status of later changes.
