# PyPI Migration Guide: Violet Pool API

This guide describes the steps to convert the isolated API (`violet_pool_api`) from this repository into a proper PyPI package and use it officially in Home Assistant. This fully satisfies the Home Assistant "External Python Library" requirement.

## Step 1: Copy Code to Your New Repository

1. Clone your new (still empty) repository locally:
   ```bash
   git clone https://github.com/Xerolux/violet_pool_api.git
   cd violet_pool_api
   ```
2. Copy the entire CONTENTS of the `custom_components/violet_pool_controller/violet_pool_api/` folder from this (Home Assistant) repository into the new repo.
3. The structure in the new repo should then look like this:
   ```
   violet_pool_api/
   ├── violet_pool_api/
   │   ├── __init__.py
   │   ├── api.py
   │   ├── circuit_breaker.py
   │   ├── const_api.py
   │   ├── const_devices.py
   │   ├── utils_rate_limiter.py
   │   └── utils_sanitizer.py
   ├── pyproject.toml
   ├── setup.py
   └── README.md
   ```
*(Note: The templates for `pyproject.toml`, `setup.py`, and `README.md` have already been generated — see `custom_components/violet_pool_controller/violet_pool_api/`)*

## Step 2: Publish to PyPI

In the new repository `Xerolux/violet_pool_api`:

1. Create an account on [PyPI](https://pypi.org/).
2. Install the required build tools:
   ```bash
   pip install build twine
   ```
3. Build the package:
   ```bash
   python3 -m build
   ```
4. Upload it to PyPI:
   ```bash
   python3 -m twine upload dist/*
   ```
   *(You will be prompted for your PyPI token)*

**Tip:** Alternatively, you can set up a simple GitHub Action in the new repo that automatically pushes the package to PyPI on each new release!

## Step 3: Update the Home Assistant Integration

Once the package is available on PyPI under the name `violet-pool-api` (e.g. version `1.0.0`), return to this repository (`violet-hass`) and do the following:

1. **Delete the folder:** Remove the entire `custom_components/violet_pool_controller/violet_pool_api/` directory.
2. **Update the manifest:** Open `custom_components/violet_pool_controller/manifest.json` and add your package as a dependency:
   ```json
   "requirements": [
       "violet-pool-api==1.0.0"
   ]
   ```
3. **Test imports:** Home Assistant will now automatically download the package from PyPI. Since all imports in the integration have already been changed to `from violet_pool_api.xxx import ...`, everything will continue to work out of the box! (You may need to change `from .violet_pool_api.api` to `from violet_pool_api.api` in the HA files if relative imports were used).
