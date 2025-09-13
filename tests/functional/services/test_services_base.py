import pytest

from mtgcobuilderapi.common.exceptions import InvalidServiceDefinitionError
from mtgcobuilderapi.config.settings.base import ServiceAbstractConfigurationBase
from tests.common.services import MOCK_SERVICE_SETTINGS, MockConfiguration, MockService

from typing import Generator


@pytest.mark.offline
def test_configuration_context_manager(mock_service_environment: Generator[None, None, None]) -> None:
    with MockConfiguration.use() as config:
        for setting_name, setting_value in MOCK_SERVICE_SETTINGS.items():
            assert getattr(config, setting_name) == setting_value


@pytest.mark.offline
def test_initializing_mock_service(mock_service_environment: Generator[None, None, None]) -> None:
    initialized_mock_service = MockService()
    assert initialized_mock_service.message == MockService.construct_message(
        MOCK_SERVICE_SETTINGS["mock_setting"], str(MOCK_SERVICE_SETTINGS["another_mock_setting"])
    )


@pytest.mark.offline
def test_type_error_on_invalid_service_subclass(mock_service_environment: Generator[None, None, None]) -> None:
    with pytest.raises(InvalidServiceDefinitionError) as exc_info:

        class InvalidService(MockService): ...

    assert "must define a config model" in str(exc_info.value), (
        "Expected TypeError for missing config attribute in subclass."
    )

    with pytest.raises(InvalidServiceDefinitionError) as exc_info:

        class AnotherInvalidService(MockService, config="InvalidConfig"):  # type: ignore
            ...

    assert f"must inherit from {ServiceAbstractConfigurationBase.__name__}" in str(exc_info.value), (
        "Expected TypeError for missing config attribute in subclass."
    )
