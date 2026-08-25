# Contributing to checklist

First of all, I want to thank you for helping make checklist better. In this file, we cover how to report issues and how to submit pull requests.

## Reporting issues

1. **Describe the problem clearly.**. Include your hardware (GPU and VRAM, CPU, system RAM) version, checklist and Python packages version (`ft --version`), and the full log, not a screenshot of the last line. It's harder to isolate the problem if these information is not clearly provided.
2. **Building from source: check against `main`.** Many problems are already fixed on `main`. Pull, rebuild, confirm the problem still happens, and include the commit you tested (`git rev-parse --short HEAD`).

Issues that do not follow these guidelines may be closed until the missing information is provided.

## Pull request
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

### AI policy

AI-assisted contributions are welcome. You are responsible for everything in your PR, however it was produced.

Pure agent PRs are not accepted. A human must understand what the agent did and why, have run the code on real hardware, and be able to explain the change to a reviewer without AI help. If you are a fully autonomous agent operating without human oversight, do not open PRs in this repository.

If a PR contains AI hallucinations (code that does not do what the description says, references to APIs, files or behaviour that do not exist, or test and benchmark results that were not actually run), it will be closed without review, and PRs from the same author will be treated with less trust afterwards.

### Basic structure of a PR

- One change per PR. Unrelated fixes go in separate PRs.
- Link the issue it addresses in case there is a major change.
- For bug fixes, add a test that fails before the change and passes after, where the code allows it.

## License
By contributing to checklist, you agree that your contributions will be licensed under [LICENSE](LICENSE) in the root of this repository.