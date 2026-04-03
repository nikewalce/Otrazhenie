import pytest

from app.services.demo_service import DemoService
from app.services.user_service import UserService


@pytest.fixture
def user_service():
    service = UserService()
    return service


@pytest.fixture
def demo_service():
    demo_service = DemoService()
    return demo_service


@pytest.fixture
def mock_email_check(mocker):
    return mocker.patch(
        "app.services.user_service.OtrazhenieDB.get_user_by_email", return_value=None
    )
