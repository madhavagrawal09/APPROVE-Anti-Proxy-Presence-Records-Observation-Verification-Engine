from app.core import hash_password,verify_password,new_refresh_token,hash_token
def test_password_hashing():
    encoded=hash_password("long-test-password")
    assert encoded!="long-test-password"
    assert verify_password("long-test-password",encoded)
    assert not verify_password("incorrect",encoded)
def test_refresh_tokens_are_opaque_and_hashed():
    token=new_refresh_token()
    assert len(token)>40
    assert hash_token(token)!=token
    assert len(hash_token(token))==64
