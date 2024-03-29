"""Admin API endpoint functions.

All endpoints require administrative privileges.
"""
import config
import errors
from db import models
from utils import authenticator
from utils import handler


def deleteUser():
    """Delete a user by id.

    :field id [int]: user id
    :raises UnprocessableRequest: if no users exists with the id
    """
    authenticator.authenticate(admin=True)
    userId = handler.parse('id', int)

    # Get user from database
    user = models.User.query.filter_by(id=userId).first()
    if not user:
        raise errors.UnprocessableRequest(f'no user found with id {userId}')

    # Delete all stuff owned by user
    for stuff in models.Stuff.query.filter_by(user_id=user.id).all():
        stuff.delete()

    user.delete()


def getAllStuff():
    """Get all existing stuff.

    :returns [list]: stuff as dicts
    """
    authenticator.authenticate(admin=True)
    return [entry.dict() for entry in models.Stuff.query.all()]


def getBlacklistedTokens():
    """Get all blacklisted auth tokens.

    :returns [list]: blacklisted tokens
    """
    authenticator.authenticate(admin=True)
    return [token.dict().get('token')
            for token in models.AuthTokenBlacklist.query.all()]


def getAllUsers():
    """Get all existing users.

    :returns [list]: user info as dicts
    """
    authenticator.authenticate(admin=True)
    return [user.dict() for user in models.User.query.all()]


def getUser():
    """Get user by id.

    :field id [int]: user id
    :returns [dict]: user info
    :raises UnprocessableRequest: if no users exists with the id
    """
    authenticator.authenticate(admin=True)
    userId = handler.parse('id', int)

    # Get user from database
    user = models.User.query.filter_by(id=userId).first()
    if not user:
        raise errors.UnprocessableRequest(f'no user found with id {userId}')

    return user.dict()
