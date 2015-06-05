# TracToChatwork
Trac notification plugin for Chatwork

## Setting

trac.ini
```
[tochatwork]
# chatwork api base url (required)
api_base_url = https://api.chatwork.com/v1

# notification account (required)
api_token = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# notificaiton room (required)
room_id = 00000000

# notify only when ticket owner has been changed (default: false)
only_owner_changed = true|false

# force notification if included in the comments
notify_symbol = @cw

# account custom field name for api token
api_token_field_name = chatwork_api_token
```
