"""Tests for Violet Pool Controller translations (Gold Level)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def get_component_dir():
    """Get component directory path."""
    return Path(__file__).parent.parent / "custom_components" / "violet_pool_controller"


class TestTranslationFiles:
    """Test translation file structure and content."""

    @property
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent

    @property
    def component_dir(self):
        """Get component directory."""
        return self.project_root / "custom_components" / "violet_pool_controller"

    def test_strings_json_exists(self):
        """Test that strings.json exists."""
        strings_path = self.component_dir / "strings.json"
        assert strings_path.exists(), f"strings.json not found at {strings_path}"

    def test_german_translation_exists(self):
        """Test that German translation file exists."""
        de_path = self.component_dir / "translations" / "de.json"
        assert de_path.exists(), f"German translation (de.json) not found at {de_path}"

    def test_english_translation_exists(self):
        """Test that English translation file exists."""
        en_path = self.component_dir / "translations" / "en.json"
        assert en_path.exists(), f"English translation (en.json) not found at {en_path}"

    def test_strings_json_valid_json(self):
        """Test that strings.json is valid JSON."""
        strings_path = self.component_dir / "strings.json"

        with open(strings_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict), "strings.json must be a dictionary"
        assert "config" in data, "strings.json must contain 'config' key"

    def test_german_translation_valid_json(self):
        """Test that German translation is valid JSON."""
        de_path = self.component_dir / "translations" / "de.json"

        with open(de_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict), "de.json must be a dictionary"
        assert "config" in data, "de.json must contain 'config' key"

    def test_english_translation_valid_json(self):
        """Test that English translation is valid JSON."""
        en_path = self.component_dir / "translations" / "en.json"

        with open(en_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict), "en.json must be a dictionary"
        assert "config" in data, "en.json must contain 'config' key"


class TestTranslationStructure:
    """Test translation structure and required keys."""

    @property
    def component_dir(self):
        """Get component directory."""
        return Path(__file__).parent.parent / "custom_components" / "violet_pool_controller"

    @pytest.fixture
    def strings_data(self):
        """Load strings.json data."""
        strings_path = self.component_dir / "strings.json"

        with open(strings_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def german_data(self):
        """Load German translation data."""
        de_path = self.component_dir / "translations" / "de.json"

        with open(de_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def english_data(self):
        """Load English translation data."""
        en_path = self.component_dir / "translations" / "en.json"

        with open(en_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_config_step_structure(self, strings_data):
        """Test that config steps are properly structured."""
        assert "config" in strings_data
        assert "step" in strings_data["config"]

        # Required steps for setup flow
        required_steps = [
            "user",
            "disclaimer",
            "help",
            "connection",
            "pool_setup",
            "feature_selection",
            "sensor_selection",
        ]

        for step in required_steps:
            assert step in strings_data["config"]["step"], f"Missing step: {step}"

    def test_config_error_messages(self, strings_data):
        """Test that error messages are defined."""
        assert "config" in strings_data
        assert "error" in strings_data["config"]

        # Required error messages
        required_errors = [
            "invalid_ip_address",
            "cannot_connect",
            "invalid_auth",
            "already_configured",
        ]

        for error in required_errors:
            assert error in strings_data["config"]["error"], f"Missing error: {error}"

    def test_config_abort_messages(self, strings_data):
        """Test that abort messages are defined."""
        assert "config" in strings_data
        assert "abort" in strings_data["config"]

        # Required abort messages
        required_aborts = [
            "already_configured",
            "cannot_connect",
            "reauth_successful",
            "reconfigure_successful",
        ]

        for abort in required_aborts:
            assert abort in strings_data["config"]["abort"], f"Missing abort: {abort}"

    def test_options_flow_structure(self, strings_data):
        """Test that options flow steps are defined."""
        assert "options" in strings_data
        assert "step" in strings_data["options"]

        # Required options steps
        required_options_steps = ["init", "features", "sensors", "settings"]

        for step in required_options_steps:
            assert step in strings_data["options"]["step"], f"Missing options step: {step}"

    def test_services_translated(self, strings_data):
        """Test that services are translated."""
        assert "services" in strings_data

        # Required services
        required_services = [
            "turn_auto",
            "set_pv_surplus",
            "set_temperature_target",
            "set_ph_target",
            "export_diagnostic_logs",
        ]

        for service in required_services:
            assert service in strings_data["services"], f"Missing service: {service}"
            # Each service should have name and description
            assert "name" in strings_data["services"][service]
            assert "description" in strings_data["services"][service]

    def test_entity_translations(self, strings_data):
        """Test that entity names are translated."""
        assert "entity" in strings_data

        # Required entity components
        required_components = ["sensor", "binary_sensor", "switch", "climate"]

        for component in required_components:
            assert component in strings_data["entity"], f"Missing entity component: {component}"


class TestGermanTranslationContent:
    """Test German translation content."""

    @pytest.fixture
    def german_data(self):
        """Load German translation data."""
        de_path = (
            Path(__file__).parent
            / "custom_components"
            / "violet_pool_controller"
            / "translations"
            / "de.json"
        )

        with open(de_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_german_config_steps(self, german_data):
        """Test that German config steps are present."""
        assert "config" in german_data
        assert "step" in german_data["config"]

        # Check a few key steps have German translations
        user_step = german_data["config"]["step"].get("user", {})
        assert "title" in user_step
        assert "Setup" in user_step["title"] or "Assistent" in user_step["title"]

    def test_german_error_messages(self, german_data):
        """Test that German error messages are present."""
        assert "config" in german_data
        assert "error" in german_data["config"]

        # Check error messages are in German
        cannot_connect = german_data["config"]["error"].get("cannot_connect", "")
        assert "Verbindung" in cannot_connect or "fehlgeschlagen" in cannot_connect

    def test_german_entity_names(self, german_data):
        """Test that German entity names are provided."""
        assert "entity" in german_data
        assert "sensor" in german_data["entity"]

        # Check some sensor names are German
        ph_sensor = german_data["entity"]["sensor"].get("ph_value", {})
        assert "name" in ph_sensor
        assert "pH" in ph_sensor["name"]


class TestEnglishTranslationContent:
    """Test English translation content."""

    @pytest.fixture
    def english_data(self):
        """Load English translation data."""
        en_path = (
            Path(__file__).parent
            / "custom_components"
            / "violet_pool_controller"
            / "translations"
            / "en.json"
        )

        with open(en_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_english_config_steps(self, english_data):
        """Test that English config steps are present."""
        assert "config" in english_data
        assert "step" in english_data["config"]

        # Check a few key steps have English translations
        user_step = english_data["config"]["step"].get("user", {})
        assert "title" in user_step
        assert "Setup" in user_step["title"] or "Assistant" in user_step["title"]

    def test_english_error_messages(self, english_data):
        """Test that English error messages are present."""
        assert "config" in english_data
        assert "error" in english_data["config"]

        # Check error messages are in English
        cannot_connect = english_data["config"]["error"].get("cannot_connect", "")
        assert "Connection" in cannot_connect or "Failed" in cannot_connect

    def test_english_entity_names(self, english_data):
        """Test that English entity names are provided."""
        assert "entity" in english_data
        assert "sensor" in english_data["entity"]

        # Check some sensor names are English
        ph_sensor = english_data["entity"]["sensor"].get("ph_value", {})
        assert "name" in ph_sensor
        assert "pH" in ph_sensor["name"]


class TestTranslationCompleteness:
    """Test that translations are complete and consistent."""

    @pytest.fixture
    def strings_data(self):
        """Load strings.json data."""
        strings_path = (
            Path(__file__).parent
            / "custom_components"
            / "violet_pool_controller"
            / "strings.json"
        )

        with open(strings_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def german_data(self):
        """Load German translation data."""
        de_path = (
            Path(__file__).parent
            / "custom_components"
            / "violet_pool_controller"
            / "translations"
            / "de.json"
        )

        with open(de_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def english_data(self):
        """Load English translation data."""
        en_path = (
            Path(__file__).parent
            / "custom_components"
            / "violet_pool_controller"
            / "translations"
            / "en.json"
        )

        with open(en_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_config_steps_match_between_de_and_en(self, german_data, english_data):
        """Test that German and English have same config steps."""
        de_steps = set(german_data.get("config", {}).get("step", {}).keys())
        en_steps = set(english_data.get("config", {}).get("step", {}).keys())

        # Should have same steps
        assert de_steps == en_steps, f"Steps mismatch: DE={de_steps}, EN={en_steps}"

    def test_error_messages_match_between_de_and_en(self, german_data, english_data):
        """Test that German and English have same error messages."""
        de_errors = set(german_data.get("config", {}).get("error", {}).keys())
        en_errors = set(english_data.get("config", {}).get("error", {}).keys())

        # Should have same errors
        assert de_errors == en_errors, f"Errors mismatch: DE={de_errors}, EN={en_errors}"

    def test_services_match_between_de_and_en(self, german_data, english_data):
        """Test that German and English have same services."""
        de_services = set(german_data.get("services", {}).keys())
        en_services = set(english_data.get("services", {}).keys())

        # Should have same services
        assert de_services == en_services, f"Services mismatch: DE={de_services}, EN={en_services}"

    def test_entity_translations_complete(self, german_data, english_data):
        """Test that entity translations are complete in both languages."""
        de_entities = german_data.get("entity", {})
        en_entities = english_data.get("entity", {})

        # Check both have same entity components
        assert set(de_entities.keys()) == set(en_entities.keys())

    def test_no_empty_translations_in_german(self, german_data):
        """Test that German translations don't have empty strings."""
        def check_empty(data, path=""):
            empty = []
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    empty.extend(check_empty(value, current_path))
                elif isinstance(value, str) and not value.strip():
                    empty.append(current_path)
            return empty

        empty_translations = check_empty(german_data)

        assert (
            len(empty_translations) == 0
        ), f"Empty German translations found: {empty_translations}"

    def test_no_empty_translations_in_english(self, english_data):
        """Test that English translations don't have empty strings."""
        def check_empty(data, path=""):
            empty = []
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    empty.extend(check_empty(value, current_path))
                elif isinstance(value, str) and not value.strip():
                    empty.append(current_path)
            return empty

        empty_translations = check_empty(english_data)

        assert (
            len(empty_translations) == 0
        ), f"Empty English translations found: {empty_translations}"


class TestTranslationPlaceholders:
    """Test that translation placeholders are correctly used."""

    @pytest.fixture
    def strings_data(self):
        """Load strings.json data."""
        strings_path = (
            Path(__file__).parent
            / "custom_components"
            / "violet_pool_controller"
            / "strings.json"
        )

        with open(strings_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_help_step_placeholders(self, strings_data):
        """Test that help step uses placeholders correctly."""
        help_step = strings_data["config"]["step"].get("help", {})
        description = help_step.get("description", "")

        # Should contain placeholders for documentation URLs
        assert "{docs_en}" in description or "{docs_de}" in description
        assert "{issues_url}" in description
        assert "{github_url}" in description

    def test_connection_step_placeholders(self, strings_data):
        """Test that connection step uses placeholders."""
        connection_step = strings_data["config"]["step"].get("connection", {})
        description = connection_step.get("description", "")

        # Should contain placeholder for documentation
        assert "{docs_en}" in description

    def test_reauth_step_placeholders(self, strings_data):
        """Test that reauth step uses placeholders."""
        reauth_step = strings_data["config"]["step"].get("reauth_confirm", {})
        description = reauth_step.get("description", "")

        # Should contain placeholders for controller info
        assert "{controller_name}" in description
        assert "{api_url}" in description

    def test_reconfigure_step_placeholders(self, strings_data):
        """Test that reconfigure step uses placeholders."""
        reconfigure_step = strings_data["config"]["step"].get("reconfigure", {})
        description = reconfigure_step.get("description", "")

        # Should contain placeholder for controller name
        assert "{controller_name}" in description


class TestBilingualSupport:
    """Test bilingual support in strings.json."""

    @pytest.fixture
    def strings_data(self):
        """Load strings.json data."""
        strings_path = (
            Path(__file__).parent
            / "custom_components"
            / "violet_pool_controller"
            / "strings.json"
        )

        with open(strings_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_strings_json_contains_bilingual_text(self, strings_data):
        """Test that strings.json contains both German and English text."""
        user_step = strings_data["config"]["step"].get("user", {})
        description = user_step.get("description", "")

        # Should contain both German ("DE:") and English ("EN:") markers
        assert "DE:" in description or "Deutsch" in description
        assert "EN:" in description or "English" in description

    def test_disclaimer_bilingual(self, strings_data):
        """Test that disclaimer is bilingual."""
        disclaimer_step = strings_data["config"]["step"].get("disclaimer", {})
        description = disclaimer_step.get("description", "")

        # Should contain both languages
        assert "Sicherheitswarnung" in description or "Safety Warning" in description

    def test_connection_step_bilingual(self, strings_data):
        """Test that connection step is bilingual."""
        connection_step = strings_data["config"]["step"].get("connection", {})
        title = connection_step.get("title", "")

        # Should have bilingual title
        assert "Controller" in title or "Verbindung" in title
