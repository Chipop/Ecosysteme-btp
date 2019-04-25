from django.utils import timezone
from datetime import timedelta
import jwt
import json
import requests
from SocialNetworkJob import settings

PUSHER_INSTANCE_LOCATOR = settings.PUSHER_INSTANCE_LOCATOR
PUSHER_SECRET_KEY = settings.PUSHER_SECRET_KEY
PUSHER_INSTANCE_ID = settings.PUSHER_INSTANCE_ID
PUSHER_KEY_ID = settings.PUSHER_KEY_ID
PUSHER_SECRET = settings.PUSHER_SECRET

PUSHER_CHATKIT_SUPERADMIN_ID = settings.PUSHER_CHATKIT_SUPERADMIN_ID

CREATED_AT = timezone.localtime() - timedelta(hours=5)
EXPIRES_AT = CREATED_AT + timedelta(hours=12)


def pusher_create_user(request, id, name, avatar_url=None, custom_data=None):
    user_json = {
        'id': str(id),
        'name': name,
    }

    headers = {'Authorization': "Bearer " + pusher_get_jwt_token(PUSHER_CHATKIT_SUPERADMIN_ID, su=True)}

    r = requests.post('https://us1.pusherplatform.io/services/chatkit/v2/' + PUSHER_INSTANCE_ID + "/users/",
                      data=json.dumps(user_json), headers=headers)

    print(r.text)


def pusher_create_room(request,room_creator_id, user_ids):

    room_json = {
        'user_ids': user_ids,  # = Array ["1","2"]
        'private': True
    }

    headers = {'Authorization': "Bearer " + pusher_get_jwt_token(room_creator_id, su=True)}

    r = requests.post('https://us1.pusherplatform.io/services/chatkit/v2/' + PUSHER_INSTANCE_ID + "/rooms/",
                      data=json.dumps(room_json), headers=headers)

    print(r.text)


def pusher_get_jwt_token(userid, su=False):
    # https://docs.pusher.com/chatkit/authentication#generating-your-own-tokens

    payload = {
        "instance": PUSHER_INSTANCE_ID,
        "iss": "api_keys/" + PUSHER_KEY_ID,
        "iat": CREATED_AT,
        "exp": EXPIRES_AT,
        "sub": str(userid)  # User  Id
    }

    if su == True:
        payload['su'] = True

    return jwt.encode(payload, PUSHER_SECRET, algorithm='HS256').decode("utf-8")


def pusher_get_jwt_token_response(userid, su=False):
    encoded_token = pusher_get_jwt_token(userid)

    response = {
        'access_token': encoded_token,
        'user_id': str(userid),
        'expires_in': EXPIRES_AT,
    }

    return response
