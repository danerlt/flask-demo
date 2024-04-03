#!/usr/bin/env python  
# -*- coding:utf-8 -*-  

import logging
from datetime import datetime
from functools import wraps

from flask import request
from flask_restful import Resource
from werkzeug.exceptions import Unauthorized

from extensions.ext_db import db
from models.account import ApiToken
from services.account_service import AccountService

logger = logging.getLogger(__name__)


def validate_and_get_api_token():
    """
    Validate and get API token.
    """
    api_key = request.args.get('apikey')
    if not api_key:
        raise Unauthorized("API KEY can't be empty")

    api_token = db.session.query(ApiToken) \
        .filter(ApiToken.token == api_key) \
        .first()

    if not api_token:
        raise Unauthorized("Access token is invalid")

    api_token.last_used_at = datetime.utcnow()
    db.session.commit()

    return api_token


def validate_apikey(view=None):
    def decorator(view):
        @wraps(view)
        def decorated(*args, **kwargs):
            try:
                api_token = validate_and_get_api_token()
                account_id = api_token.account_id
                account = AccountService.load_user(account_id)
                if account:
                    # TODO 这个需要和 flask login 插件结合
                    pass
                    # current_app.login_manager._update_request_context_with_user(account)
                    # user_logged_in.send(current_app._get_current_object(), user=_get_user())
                else:
                    raise Unauthorized("Account does not exist.")
            except Exception as e:
                logger.exception("validate_token error: {str(e)}")
                raise Unauthorized(str(e))
            else:
                return view(account.id, *args, **kwargs)

        return decorated

    if view:
        return decorator(view)

    # if view is None, it means that the decorator is used without parentheses
    # use the decorator as a function for method_decorators
    return decorator


class ApiResource(Resource):
    method_decorators = [validate_apikey]
