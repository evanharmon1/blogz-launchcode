from hashutils import make_pw_hash, check_pw_hash

def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check if email is defined correctly and that the plain text password is correct
    """
    assert new_user.username == "telosmachina"
    assert new_user.pw_hash == "1234secret"

def test_password_hash(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check if the password is hashed correctly with the make_pw_hash function
    """

    unhashed_pw = new_user.pw_hash
    salted_hash = make_pw_hash(new_user.pw_hash)

    assert salted_hash != None
    assert salted_hash != unhashed_pw
    assert "," in salted_hash

def test_password_verification(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check if the actual password can be verified against the password hash + salt
    """

    assert check_pw_hash("1234secret", make_pw_hash(new_user.pw_hash)) == True