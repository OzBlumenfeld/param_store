import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.encryption import EncryptionService
from app.services.parameter_service import ParameterService

@pytest.fixture
def db_session(test_db: Session) -> Session:
    # Create a test user
    user = User(username="testuser", hashed_password="fakehashedpassword")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    return test_db


@pytest.fixture
def encryption_service() -> EncryptionService:
    return EncryptionService(master_key_str="test-master-key")


@pytest.fixture
def parameter_service(
    db_session: Session, encryption_service: EncryptionService
) -> ParameterService:
    return ParameterService(db=db_session, encryption_service=encryption_service)


def test_set_and_get_parameter(parameter_service: ParameterService, db_session: Session):
    user = db_session.query(User).filter_by(username="testuser").first()
    app = "test_app"
    name = "test_param"
    value = "super-secret-123"

    # 1. Set parameter
    param = parameter_service.set_parameter(user.id, app, name, value)
    assert param.name == name
    assert param.app == app
    assert param.user_id == user.id

    # 2. Get parameter (decrypted)
    retrieved_value = parameter_service.get_parameter(user.id, name, app)
    assert retrieved_value == value


def test_update_parameter(parameter_service: ParameterService, db_session: Session):
    user = db_session.query(User).filter_by(username="testuser").first()
    app = "test_app"
    name = "updatable_param"
    value1 = "first-value"
    value2 = "second-value"

    # Set initial value
    parameter_service.set_parameter(user.id, app, name, value1)

    # Update with new value
    parameter_service.set_parameter(user.id, app, name, value2)

    # Verify retrieved value is updated
    retrieved_value = parameter_service.get_parameter(user.id, name, app)
    assert retrieved_value == value2


def test_get_nonexistent_parameter(parameter_service: ParameterService, db_session: Session):
    user = db_session.query(User).filter_by(username="testuser").first()
    assert parameter_service.get_parameter(user.id, "does_not_exist") is None

def test_user_isolation(parameter_service: ParameterService, db_session: Session):
    # Create another user
    user2 = User(username="user2", hashed_password="fakehashedpassword")
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)
    
    user1 = db_session.query(User).filter_by(username="testuser").first()
    
    app = "shared_app"
    name = "shared_name"
    
    # User 1 sets a param
    parameter_service.set_parameter(user1.id, app, name, "secret1")
    
    # User 2 sets same param name/app
    parameter_service.set_parameter(user2.id, app, name, "secret2")
    
    # Verify they are separate
    assert parameter_service.get_parameter(user1.id, name, app) == "secret1"
    assert parameter_service.get_parameter(user2.id, name, app) == "secret2"
