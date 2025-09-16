# Manage a Providers Data

[![Ministry of Justice Repository Compliance Badge](https://github-community.service.justice.gov.uk/repository-standards/api/template-repository/badge)](https://github-community.service.justice.gov.uk/repository-standards/template-repository)

A flask application for managing legal aid providers' data.

# Getting started

## Local installation for development:

### Setup

Create a virtual environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:
```
pip install -r requirements/generated/requirements-development.txt
```

### Assets setup

For this you'll need to install node > v20.9.0.

```bash
nvm install --lts
nvm use --lts
```

```bash
npm install
```

Once installed you now have access to GOVUK components, stylesheets and JS via the `node_module`

To copy some of the assets you'll need into your project, run the following:

```bash
npm run build
```

Ensure you do this before starting your Flask project as you're JS and SCSS imports will fail in the flask run.

### Configuration environment variables

Create your local config file `.env` from the template file:

```shell
cp .env.example .env
```

Don't worry, you can't commit your `.env` file.

### Run the service

Add `redis://localhost:6379/0` as the REDIS_URL in your .env file

start redis using

```
docker compose up -d redis
```

In another terminal wndow run:

```shell
source .venv/bin/activate
flask --app app run --debug --port=8020
```

Now you can browse: http://127.0.0.1:8020

(The default port for flask apps is 5000, but on Macs this is often found to conflict with Apple's Airplay service, hence using another port here.)

## Running in Docker

For local development and deployments, run the below code to create and run the Manage a Provider's Data container image.

```shell
./run_local.sh
```

## Testing

To run all the tests:

```shell
pytest
```

To run unit tests:

```shell
pytest tests/unit_tests
```

To run functional/non-functional tests:

```shell
pytest tests/functional_tests
```

Run tests in headed mode:

```shell
pytest --headed
```

Run tests in a different browser (chromium, firefox, webkit):

```shell
pytest --browser firefox
```

Run tests in multiple browsers:

```shell
pytest --browser chromium --browser webkit
```

If you are running into issues where it states a browser needs to be installed run:

```shell
playwright install
```

For further guidance on writing tests https://playwright.dev/python/docs/writing-tests

## Code formatting and linting
The following will:
- Generate requirement.txt files from files inside requirements/source/*.in and put them into requirements/generated/*.txt
- Run linting checks with ruff
- Run secret detection via trufflehog3

```shell
pre-commit install
```
### Manually running linting
The Ruff linter looks for code quality issues. Ensure there are no ruff issues before committing. 

To lint all files in the directory, run:

```shell
ruff check
```

To format all files in the directory, run:
```shell
ruff format
```

## Dependency management
Requirements listed in the `requirements/source/*.in` files should not be pinned by default.

If a release is incompatible then this can be specified using `requirement!=1.0.5`, or `requirement<2.0`.

Using this method allows for `pip-tools` to resolve the latest compatible versions of all dependencies, making dependency updates easier.

### How to update dependencies
```bash
make update-deps
```
This will update the pinned version of the all the requirements in `requirements/generated/*.txt` using the latest version
allowed by the corresponding `requirements/source/*.in` file.
By pinning every dependency in these generated files we can be sure all environments are using the same dependency versions.


## Secret scanning
We use Gitleaks for secret scanning. Gitleaks is installed as a pre-commit hook and runs as part of the static-analysis job in the CI pipeline.

If you wish to knowingly commit a test secret please add `#gitleaks:allow` to the end of the line.
For example
```python
class CustomClass:
    client_secret = "8dyfuiRyq=vVc3RRr_edRk-fK__JItpZ"  #gitleaks:allow
```

## Authentication and Authorization

Authentication is implemented using **Microsoft Entra ID Single Sign-On (SSO)**.

Currently, no role-based or scoped authorization is in place. Access is granted by manually assigning users to the associated **Entra ID enterprise application**.

Members of the development team have the necessary permissions to manage user assignments directly via the **Microsoft Entra ID portal**.

### Packages Used

- [**flask_session**](https://pypi.org/project/Flask-Session/)
  Handles server-side session storage. We use a Redis backend to persist user session data.

- [**ms-identity-python**](https://github.com/azure-samples/ms-identity-python)
  Provides integration with Microsoft Entra ID, including automatic registration of login and logout routes for Flask applications.

  This package was modified(by subclassing) to support our specific use cases:
  - **Logout Handling**: The default implementation had issues correctly detecting the request scheme (`http` vs `https`) for constructing the post-logout redirect URI.
  - **`login_required` Behavior**: In certain environments (e.g., local development and automated tests), we needed a way to bypass Entra ID authentication


### Business logic documentation
- [Add advocates/ barristers](docs/add-barrister-advocate.md) 