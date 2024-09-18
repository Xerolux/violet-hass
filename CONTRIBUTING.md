# Contribution Guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## GitHub is used for everything

GitHub is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using `scripts/lint`). You can run it locally by navigating to the `scripts/` folder and executing `bash lint.sh` (or any relevant command). Ensure your environment is properly set up before running this script.
4. Test your contribution. Make sure all existing tests pass, and write new tests if needed. If you're unfamiliar with testing in this project, refer to the [Testing Guide](link_to_testing_docs).
5. Issue that pull request!

## How to Contribute

1. Fork the repository and clone it to your local machine.
2. Create a new branch: `git checkout -b my-branch-name`
3. Make your changes and commit them: `git commit -m 'My detailed description'`
4. Push to your fork: `git push origin my-branch-name`
5. Submit a pull request.

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [black](https://github.com/ambv/black) to make sure the code follows the style.

## Test your code modification

This custom component is based on [integration_blueprint template](https://github.com/ludeeus/integration_blueprint).

It comes with a development environment in a container, easy to launch if you use Visual Studio Code. With this container, you will have a standalone Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml) file.

If you're unfamiliar with setting up Docker and VS Code, refer to [this guide](https://github.com/ludeeus/integration_blueprint).

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

