import pytest
import uuid as uuid_mod
from sqlalchemy.engine import default
from app.models.user import GUID
from app.db.session import get_db
from sqlalchemy.orm import Session

def test_guid_type_decorator():
    guid_type = GUID()
    dialect = default.DefaultDialect()
    
    # 1. process_bind_param
    val_uuid = uuid_mod.uuid4()
    assert guid_type.process_bind_param(val_uuid, dialect) == str(val_uuid)
    
    val_str = str(uuid_mod.uuid4())
    assert guid_type.process_bind_param(val_str, dialect) == val_str
    
    assert guid_type.process_bind_param(None, dialect) is None
    
    # 2. process_result_value
    assert guid_type.process_result_value(str(val_uuid), dialect) == val_uuid
    assert guid_type.process_result_value(None, dialect) is None

def test_get_db_session():
    db_gen = get_db()
    db_session = next(db_gen)
    
    # Verify we got a session
    assert isinstance(db_session, Session)
    
    # Verify it closes cleanly
    with pytest.raises(StopIteration):
        next(db_gen)
