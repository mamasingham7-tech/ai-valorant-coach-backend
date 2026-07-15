import pytest
import datetime
from jose import jwt
from app.shared.security.tokens import create_access_token, create_refresh_token, decode_token
from app.core.redis import register_refresh_token, verify_and_rotate_token, revoke_token_family
from app.core.config import settings

def test_jwt_generation_and_decoding():
    user_id = "test-user-id"
    access = create_access_token({"sub": user_id})
    refresh = create_refresh_token({"sub": user_id})
    
    payload = decode_token(access)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    
    ref_payload = decode_token(refresh)
    assert ref_payload["sub"] == user_id
    assert ref_payload["type"] == "refresh"

def test_invalid_and_malformed_tokens():
    with pytest.raises(ValueError):
        decode_token("invalid-malformed-token-string")

def test_expired_tokens():
    # Generate an expired token
    payload = {
        "sub": "test",
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token(token)

def test_refresh_token_rotation_and_reuse():
    user_id = "user-123"
    family_id = "family-xyz"
    token1 = create_refresh_token({"sub": user_id})
    
    register_refresh_token(user_id, token1, family_id, 3600)
    
    # First rotation succeeds
    u_id, fam_id = verify_and_rotate_token(token1)
    assert u_id == user_id
    assert fam_id == family_id
    
    # Subsequent rotation of the same token raises reuse exception
    with pytest.raises(ValueError, match="Token reuse detected, entire family revoked"):
        verify_and_rotate_token(token1)

def test_token_family_revocation():
    user_id = "user-456"
    family_id = "family-abc"
    token1 = create_refresh_token({"sub": user_id})
    
    register_refresh_token(user_id, token1, family_id, 3600)
    
    # Explicit revocation of token family
    revoke_token_family(token1)
    
    with pytest.raises(ValueError, match="Token family revoked"):
        verify_and_rotate_token(token1)
