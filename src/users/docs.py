GET_ALL_USERS_DOC = """
Returns a list of all users
```json
{
    "users": [
        {
            "uid": "user_6658ea62-40b4-482a-9b42-f026c4971098",
            "email": "jdoe@mail.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": true,
            "is_staff": true,
            "is_superuser": true
        },
        ...
    ]
}
```
"""

GET_USER_DETAIL_DOC = """
Returns the specific user based on uid
```json
{
    "user": {
        "uid": "user_3b8c5189-30f7-4652-9588-e99320f8ca04",
        "email": "admin@mail.com",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2025-01-07T17:08:31.867648+07:00",
        "updated_at": "2025-01-08T06:38:49.658729+07:00",
        "is_active": true,
        "is_superuser": false,
        "is_staff": true,
        "date_joined": "2025-01-07T17:08:31.646945+07:00",
        "last_login": null,
        "groups": [],
        "user_permissions": []
    }
}
```
"""

GET_USER_PERMISSIONS_DOC = """
Returns all the permissions a user has per model.
perms_ids and perms are just the reverse of each other
```json
{
    "permissions": {
        "demo": {
            "countryprofile": {
                "id": 15,
                "perms_ids": {
                    "57": "view"
                },
                "perms": {
                    "view": 57
                }
            },
            "demomodel": {
                "id": 9,
                "perms_ids": {
                    "36": "view"
                },
                "perms": {
                    "view": 36
                }
            },
            ...,
        },
        ...,
    },
    ...
}
```
"""

LOGIN_DOC = """
Admin login. Requires the email and the password for the body and sends the refresh 
token as secure cookie. Returns:
```json
{
    "access": "<access token>"
}
```
"""

LOGOUT_DOC = """
Admin logout. Logs out the user and deletes the refresh token cookie. Returns:
```json
{
    "message": "Logged out successfully."
}
```
"""

SEND_PASSWORD_RESET_LINK_DOC = """
Sends the password reset link based on user uid. Returns
```json
{
    "success": true,
    "message": "Password reset link has been sent to the email of the user"
}
```
"""

VERIFY_PASSWORD_RESET_LINK_DOC = """
Checks whether the password reset link is valid. Returns:
```json
{
    "valid": true, 
    "message": "Token is valid."
}
```
"""

RESET_PASSWORD_VIA_LINK_DOC = """
Resets the password of the user from reset link. Returns:
```json
{
    "success": true, 
    "message": "Successfully updated password"
}
```
"""