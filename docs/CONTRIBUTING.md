# Contribution Guidelines

We welcome contributions to this project!  Whether it's reporting a bug, discussing the code, submitting a fix, or proposing new features, your contributions are highly appreciated.

## How We Use GitHub

We use GitHub for everything:

*   **Code Hosting:** The project's codebase is hosted on GitHub.
*   **Issue Tracking:**  Bugs and feature requests are tracked as GitHub issues.
*   **Pull Requests:**  Code changes are submitted via pull requests.

## Pull Request Process

The best way to propose changes is through pull requests.  Here's the recommended workflow:

1.  **Fork the Repository:**  Create a fork of the repository on your GitHub account.
2.  **Create a Branch:**  From your fork, create a new branch based on the `main` branch.  Use a descriptive name for your branch (e.g., `fix/issue-123`, `feat/add-new-sensor`).
3.  **Make Changes:**  Implement your changes, including code modifications, documentation updates, and tests.
4.  **Update Documentation:** If you've added or changed functionality, update the `README.md` and any other relevant documentation.
5.  **Lint Your Code:**  Ensure your code adheres to our coding style.  Run the linter locally using the provided script:
    ```bash
    cd scripts/
    bash lint.sh
    ```
    Make sure you have the necessary development environment set up before running the linter.  This usually involves having Python and the required packages (like `black`, `pylint`, `flake8`, etc.) installed.  If you're using the VS Code dev container, these should already be set up for you.

6.  **Test Your Changes:**  Thoroughly test your changes.  This includes:
    *   Running existing tests:  The project includes a test suite.  Make sure all existing tests pass.
    *   Writing new tests: If you've added new functionality, write new tests to cover it.

7.  **Commit Your Changes:**  Commit your changes with clear and descriptive commit messages.  Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification if possible (e.g., `feat: Add support for XYZ`, `fix: Correct issue with ABC`).
8.  **Push to Your Fork:**  Push your branch to your forked repository on GitHub.
9.  **Create a Pull Request:**  From your fork on GitHub, create a pull request targeting the `main` branch of the original repository.  Provide a clear and concise description of your changes, including the issue number it addresses (if any).

## Testing

This project uses a development environment within a Docker container for easy testing. If you are using Visual Studio Code with the Remote - Containers extension, you can automatically launch this environment. This container provides a standalone Home Assistant instance pre-configured with the integration.

**Testing Steps (using VS Code Dev Container):**

1.  **Install Prerequisites:**  Make sure you have [Docker](https://www.docker.com/products/docker-desktop) and [Visual Studio Code](https://code.visualstudio.com/) installed, along with the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
2.  **Open in Container:**  Open the project folder in VS Code.  VS Code should detect the `.devcontainer` folder and prompt you to "Reopen in Container".  Click this button.  This will build the Docker image and start the container.
3.  **Access Home Assistant:** Once the container is running, you can access the Home Assistant instance at `http://localhost:8123`.  The integration should already be configured.
4.  **Run Tests (Optional):** To run the test suite, open a terminal *inside* the VS Code container (Terminal > New Terminal) and execute any relevant test commands.  The specific commands may vary, but often a simple `pytest` will be enough. (There are currently no specific tests defined, so you might need to add a test suite)

**Testing Steps (Manual Setup - Advanced Users):**

If you are *not* using the VS Code dev container, you'll need to manually set up a testing environment:

1.  **Install Home Assistant:** Install a development instance of Home Assistant.  See the [Home Assistant developer documentation](https://developers.home-assistant.io/docs/development_environment/) for instructions.
2.  **Install Dependencies:** Install any required Python packages (e.g., `aiohttp`, `async_timeout`, `voluptuous`).
3.  **Copy the Integration:** Copy the `violet_pool_controller` directory into the `custom_components` directory of your Home Assistant configuration.
4.  **Configure the Integration:** Configure the integration through the Home Assistant UI or by manually editing your `configuration.yaml`.
5. **Run the tests.**

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Bug Reports

We use GitHub issues to track public bugs.  Please report bugs by [opening a new issue](../../issues/new/choose).

**A Great Bug Report Includes:**

*   **Summary:** A brief, descriptive summary of the issue.
*   **Background:** Context about how you encountered the bug.
*   **Steps to Reproduce:**  Detailed, step-by-step instructions on how to reproduce the issue.  Be as specific as possible.
*   **Expected Result:** What you expected to happen.
*   **Actual Result:** What actually happened.
*   **Code Samples:** If possible, provide minimal code snippets that demonstrate the issue.
*   **Environment:**
    *   Home Assistant version.
    *   Integration version (from `manifest.json`).
    *   Violet Pool Controller firmware version (if applicable).
    *   Operating system.
*   **Logs:** Include relevant log entries from Home Assistant (Settings > System > Logs).  Enable debug logging for the integration if possible (`logger.set_level` in `configuration.yaml`).
*   **Notes:** Any additional notes, such as why you think the bug might be happening, or workarounds you've tried.

## Coding Style

This project uses [Black](https://github.com/psf/black) for code formatting.  Please ensure your code is formatted with Black before submitting a pull request.  The `lint.sh` script will automatically format your code with Black.

This improved CONTRIBUTING.md file provides much more detailed instructions for contributing to the project, including:

*   **Clearer Pull Request Process:**  Provides a step-by-step guide for creating pull requests.
*   **Testing Instructions:**  Explains how to set up a testing environment, both with and without the VS Code dev container.  This is *crucial* for ensuring that contributions don't break existing functionality.
*   **Bug Report Guidelines:**  Provides a template for writing effective bug reports, making it easier for maintainers to understand and fix issues.
*   **Coding Style:**  Specifies the use of Black for code formatting and provides instructions on how to use it.
*   **Conventional Commits:**  Suggests using Conventional Commits for commit messages.
*   **Links:** Includes links to relevant resources (Docker, VS Code, Remote - Containers, Home Assistant developer documentation, Black, Conventional Commits).

This comprehensive guide makes it much easier for new contributors to get involved and ensures that contributions are of high quality. It covers all the essential aspects of the contribution process.
