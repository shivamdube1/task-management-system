import pytest
from unittest.mock import MagicMock
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.exceptions import validation_exception_handler, generic_exception_handler

@pytest.mark.asyncio
async def test_validation_exception_handler():
    # Mock Request
    request_mock = MagicMock(spec=Request)
    
    # Mock RequestValidationError
    errors = [{"loc": ("body", "email"), "msg": "value is not a valid email address", "type": "value_error.email"}]
    exc = RequestValidationError(errors)
    
    response = await validation_exception_handler(request_mock, exc)
    
    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    
    # Check body
    import json
    body = json.loads(response.body.decode("utf-8"))
    expected_errors = [{"loc": ["body", "email"], "msg": "value is not a valid email address", "type": "value_error.email"}]
    assert body["detail"] == expected_errors

@pytest.mark.asyncio
async def test_generic_exception_handler():
    # Mock Request
    request_mock = MagicMock(spec=Request)
    
    # Exception
    exc = ValueError("Some internal database connection timeout failure")
    
    response = await generic_exception_handler(request_mock, exc)
    
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    
    # Check body does not leak details
    import json
    body = json.loads(response.body.decode("utf-8"))
    assert body["detail"] == "Internal server error"
