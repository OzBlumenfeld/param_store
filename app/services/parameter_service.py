from typing import Optional
from sqlalchemy.orm import Session
from app.models.parameter import Parameter
from app.services.encryption import EncryptionService


class ParameterService:
    def __init__(self, db: Session, encryption_service: EncryptionService) -> None:
        self.db = db
        self.encryption_service = encryption_service

    def set_parameter(self, user_id: int, app: str, name: str, value: str) -> Parameter:
        """Sets a parameter with envelope encryption."""
        dek = self.encryption_service.generate_dek()
        encrypted_value = self.encryption_service.encrypt_value(value, dek)
        encrypted_dek = self.encryption_service.encrypt_dek(dek)

        db_param = self.db.query(Parameter).filter(
            Parameter.user_id == user_id, 
            Parameter.app == app, 
            Parameter.name == name
        ).first()
        
        if db_param:
            db_param.encrypted_value = encrypted_value
            db_param.encrypted_dek = encrypted_dek
        else:
            db_param = Parameter(
                user_id=user_id,
                app=app,
                name=name,
                encrypted_value=encrypted_value,
                encrypted_dek=encrypted_dek,
            )
            self.db.add(db_param)

        self.db.commit()
        self.db.refresh(db_param)
        return db_param

    def update_parameter(self, user_id: int, app: str, name: str, value: str) -> Optional[Parameter]:
        """Updates an existing parameter."""
        db_param = self.db.query(Parameter).filter(
            Parameter.user_id == user_id, 
            Parameter.app == app, 
            Parameter.name == name
        ).first()
        
        if not db_param:
            return None

        dek = self.encryption_service.generate_dek()
        encrypted_value = self.encryption_service.encrypt_value(value, dek)
        encrypted_dek = self.encryption_service.encrypt_dek(dek)
            
        db_param.encrypted_value = encrypted_value
        db_param.encrypted_dek = encrypted_dek
        
        self.db.commit()
        self.db.refresh(db_param)
        return db_param

    def get_parameter(self, user_id: int, name: str, app: str = "default") -> Optional[str]:
        """Retrieves and decrypts a parameter."""
        db_param = self.db.query(Parameter).filter(
            Parameter.user_id == user_id,
            Parameter.name == name,
            Parameter.app == app
        ).first()
        
        if not db_param:
            return None

        dek = self.encryption_service.decrypt_dek(db_param.encrypted_dek)
        value = self.encryption_service.decrypt_value(db_param.encrypted_value, dek)

        return value

    def get_parameters_for_user(self, user_id: int, app: Optional[str] = None, name: Optional[str] = None, get_all_values: bool = False) -> list[dict[str, str]]:
        """Retrieves all parameter names for a user, with optional filtering."""
        query = self.db.query(Parameter).filter(Parameter.user_id == user_id)
        
        if app:
            query = query.filter(Parameter.app == app)
        if name:
            query = query.filter(Parameter.name.ilike(f"%{name}%"))
            
        db_params = query.all()
        return [{"name": p.name, "app": p.app, "value": self.get_parameter(user_id, p.name, p.app)} for p in db_params] if get_all_values else [{"name": p.name, "app": p.app} for p in db_params]

    def delete_param(self, user_id: int, name: str, app: str = "default") -> bool:
        db_param = self.db.query(Parameter).filter(
            Parameter.user_id == user_id,
            Parameter.name == name,
            Parameter.app == app
        ).first()
        
        if db_param:
            self.db.delete(db_param)
            self.db.commit()
            return True
        return False
