# Contributing to snk

First off, thank you for taking the time to contribute to snk! We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code contributions.

This document outlines the process and guidelines for contributing to the project to ensure that everything goes smoothly.

## Code of Conduct

Please note that this project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms. Be respectful to others in all interactions.

## A note on Snk vs Snk-CLI

Snk and Snk-CLI are sister projects. Snk is the command line tool that is used to install and manage the Snk-CLIs. Snk depends on Snk-CLI but Snk-CLI can be used without Snk. If you'd like to contribute to the Snk-CLI then you should make your changes in the snk-cli repository. If you'd like to makes changes to the way Snk installs and manages Snk-CLIs then you should make your changes in the snk repository.

## How to Contribute

### Reporting Bugs

If you find a bug in **snk**, please open an [issue](https://github.com/Wytamma/snk/issues) with a clear and detailed description of the problem. When reporting bugs, please include the following:

- A descriptive title
- Steps to reproduce the issue
- Expected and actual behavior
- Any relevant screenshots or error messages
- The environment details (e.g., OS, Python version)

### Suggesting Features

We welcome ideas to improve the project. If you have a feature request, open an [issue](https://github.com/Wytamma/snk/issues) with:

- A descriptive title
- A clear explanation of the proposed feature
- Why it would be useful for other users
- Any potential implementation details (if you have ideas on how to implement it)

### Contributing Code

We encourage code contributions that improve the functionality, performance, or readability of **snk** and **snk-cli**. To contribute code, follow these steps:

>[!note]
>The same contribution guidelines apply to both **snk** and **snk-cli**. If you are contributing to **snk-cli**, please make your changes in the [snk-cli repository](https://github.com/Wytamma/snk-cli).

#### Forking the Repository

1. Fork the repository to your GitHub account by clicking the "Fork" button at the top of the [repository page](https://github.com/Wytamma/snk).
2. Clone the fork to your local machine:

```bash
git clone https://github.com/your-username/snk.git
cd snk
```

**snk** uses [Hatch](https://hatch.pypa.io/latest/) for managing dependencies and development tasks. Activate the development environment:

```bash
hatch shell
```

#### Creating a Branch

Create a new branch for your changes. Use a descriptive branch name based on the type of contribution, such as:

- `feature/your-feature-name`
- `bugfix/issue-number-description`
- `docs/update-readme`

```bash
git checkout -b feature/your-feature-name
```

#### Making Changes

1. Make the necessary changes to the codebase.
2. Ensure that your changes are properly tested. Refer to the [Running Tests](#running-tests) section.
3. Follow the project's [Style Guide](#style-guide).
4. Update the documentation if needed.

#### Running Tests

Before submitting your changes, make sure all tests pass:

```bash
hatch runt test
```

To run tests with coverage:

```bash
hatch run cov
```

If you are adding new features, please write tests for them to ensure code quality and to help future maintainers.

#### Submitting a Pull Request

Once your changes are ready, push your branch to your fork:

```bash
git push origin feature/your-feature-name
```

Go to your fork on GitHub, and you should see an option to create a pull request (PR). Follow the instructions to open a PR. Be sure to include:

- A clear title and description of what your PR does (start with a [gitmoji](https://gitmoji.dev/))
- A reference to any related issues (e.g., `Closes #123`)
- A summary of the changes you’ve made

## Style Guide

Please follow these guidelines to keep the codebase consistent and clean:

- **Code Formatting**: Adhere to the Python [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. Use `ruff` for auto-formatting if needed:

  ```bash
  hatch run format
  ```

## Development Workflow

Here is a general development workflow for contributing to **snk**:

1. **Open an Issue**: If your contribution is significant (new feature, large refactor, etc.), discuss it first by creating an issue.
2. **Fork and Branch**: Fork the repository, create a new branch for your contribution.
3. **Make Changes**: Make your changes in the branch and commit regularly.
4. **Test Your Changes**: Ensure that existing tests pass and write new ones for your changes.
5. **Open a Pull Request**: Once you're satisfied with your changes, submit a pull request.
6. **Code Review**: Your pull request will undergo review. You may be asked to make revisions.
7. **Merge**: After approval, your pull request will be merged into the main branch.

---

Thank you again for contributing to **snk**! We appreciate your time and effort in making this project better for everyone.

