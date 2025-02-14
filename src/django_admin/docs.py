GET_MODEL_ADMIN_SETTINGS_DOC = """
Returns the model admin settings object for the specific model.
```json
{
    "model_admin_settings": {
        "model_name": "DemoModel",
        "app_label": "demo",
        "fieldsets": [
            {
                "title": "Section 1",
                "fields": [
                    "type",
                    "color",
                    "name",
                    "email",
                    "ordering",
                    "range_number",
                    "amount",
                    "comment",
                    "is_active"
                ]
            },
            {
                "title": "Section 2",
                "fields": [
                    "date",
                    "time",
                    "last_log",
                    "classification",
                    "permissions",
                    "file",
                    "image",
                    "metadata",
                    "html"
                ]
            }
        ],
        "list_display": [
            "name",
            "type",
            "color",
            "ordering",
            "is_active",
            "email",
            "date",
            "metadata",
            "html"
        ],
        "list_per_page": 5,
        "list_display_links": [
            "name"
        ],
        "search_fields": [
            "name",
            "email"
        ],
        "search_help_text": "Search by name, email",
        "list_filter": [
            "color",
            "type",
            "is_active"
        ],
        "readonly_fields": [
            "created_at",
            "updated_at"
        ],
        "ordering": [
            "-name",
            "type"
        ],
        "custom_actions": [
            {
                "func": "delete_listview",
                "label": "Delete selected records"
            }
        ],
        "autocomplete_fields": [
            "type"
        ],
        "table_filters": [
            {
                "field": "color",
                "values": [
                    {
                        "value": null,
                        "label": "All"
                    },
                    {
                        "value": "Blue",
                        "label": "Blue"
                    },
                    {
                        "value": "Red",
                        "label": "Red"
                    }
                ]
            },
            {
                "field": "type",
                "values": [
                    {
                        "value": null,
                        "label": "All"
                    },
                    {
                        "value": 1,
                        "label": "Warning"
                    },
                    {
                        "value": 2,
                        "label": "Success"
                    },
                    {
                        "value": 3,
                        "label": "Danger"
                    },
                    {
                        "value": 4,
                        "label": "Info"
                    },
                    {
                        "value": 5,
                        "label": "Dark"
                    }
                ]
            },
            {
                "field": "is_active",
                "values": [
                    {
                        "value": null,
                        "label": "All"
                    },
                    {
                        "value": true,
                        "label": "True"
                    },
                    {
                        "value": false,
                        "label": "False"
                    }
                ]
            }
        ],
        "custom_inlines": [
            {
                "app_label": "demo",
                "model_name": "demomodel",
                "model_name_label": "DemoModel",
                "list_display": [
                    "name",
                    "type",
                    "color",
                    "ordering",
                    "is_active",
                    "email"
                ],
                "list_display_links": [
                    "name"
                ],
                "list_per_page": 5
            },
            {
                "app_label": "demo",
                "model_name": "type",
                "model_name_label": "Type",
                "list_display": [
                    "name"
                ],
                "list_display_links": [
                    "name"
                ],
                "list_per_page": 3
            },
            {
                "app_label": "demo",
                "model_name": "countryprofile",
                "model_name_label": "CountryProfile",
                "list_display": [
                    "country",
                    "level",
                    "type",
                    "area"
                ],
                "list_display_links": [
                    "country"
                ],
                "list_per_page": 5
            }
        ],
        "extra_inlines": [
            "sample_extra"
        ]
    }
}
```
"""

GET_MODEL_FIELDS_DOC = """
Returns all the fields of a model including its attributes, initial values and validatiors.
On edit, pass the pk of the model record.
```json
{
    "fields": {
        "password": {
            "name": "password",
            "label": "Password",
            "is_primary_key": false,
            "max_length": 128,
            "editable": true,
            "help_text": "",
            "auto_created": false,
            "type": "CharField",
            "initial": "",
            "required": true,
            "choices": null
        },
        "uid": {
            "name": "uid",
            "label": "Uid",
            "is_primary_key": true,
            "max_length": 255,
            "editable": false,
            "help_text": "",
            "auto_created": false,
            "type": "CharField",
            "initial": "user_4743729d-25df-4162-8be7-06025ab23de2",
            "required": true,
            "choices": null
        },
        "email": {
            "name": "email",
            "label": "Email address",
            "is_primary_key": false,
            "max_length": 254,
            "editable": true,
            "help_text": "",
            "auto_created": false,
            "type": "EmailField",
            "initial": "",
            "required": true,
            "choices": null
        },
        "user_permissions": {
            "name": "user_permissions",
            "label": "User permissions",
            "is_primary_key": false,
            "max_length": null,
            "editable": true,
            "help_text": "",
            "auto_created": false,
            "type": "ManyToManyField",
            "initial": "",
            "required": false,
            "choices": null
        },
        "color": {
            "name": "color",
            "label": "Color",
            "is_primary_key": false,
            "max_length": 10,
            "editable": true,
            "help_text": "",
            "auto_created": false,
            "type": "CharField",
            "initial": "Blue",
            "required": true,
            "choices": [
                {
                    "label": "Blue",
                    "value": "Blue",
                    "selected": true
                },
                {
                    "label": "Red",
                    "value": "Red",
                    "selected": false
                }
            ]
        },
        "amount": {
            "name": "amount",
            "label": "Amount",
            "is_primary_key": false,
            "max_length": null,
            "editable": true,
            "help_text": "Max of 10 digits with format: 12345678.90",
            "auto_created": false,
            "type": "DecimalField",
            "initial": 0.0,
            "required": true,
            "choices": null,
            "regex_pattern": "^\\d{1,8}(\\.\\d{0,2})?$",
            "regex_message": "Enter a valid amount (up to 8 digits before the decimal and 2 digits",
            "max_digits": 10,
            "decimal_places": 2
        },
        "image": {
            "name": "image",
            "label": "Image",
            "is_primary_key": false,
            "max_length": 100,
            "editable": true,
            "help_text": "Allowed file types: ['.jpg', '.jpeg', '.png'] | Max file size in MB: [2]",
            "auto_created": false,
            "type": "ImageField",
            "initial": "",
            "required": true,
            "choices": null
        },
        "classification": {
            "name": "classification",
            "label": "Classification",
            "is_primary_key": false,
            "max_length": null,
            "editable": true,
            "help_text": "",
            "auto_created": false,
            "type": "ManyToManyField",
            "initial": "",
            "required": true,
            "choices": null,
            "manytomany_choices": [
                {
                    "id": 1,
                    "label": "Herbivore",
                    "checked": false
                },
                {
                    "id": 2,
                    "label": "Carnivore",
                    "checked": false
                },
                {
                    "id": 3,
                    "label": "Omnivore",
                    "checked": false
                }
            ],
            "manytomany_related_app": "demo",
            "manytomany_related_model": "Classification"
        },
        ...
    }
}
```
"""

GET_APPS_DOC = """
Returns a list of all registered apps with add and change links and permissions 
associated to the user.
```json
{
    "appList": [
        {
            "name": "Administration",
            "appLabel": "admin",
            "appUrl": "/dashboard/admin",
            "hasModulePerms": true,
            "models": [
                {
                    "name": "Log entries",
                    "objectName": "LogEntry",
                    "adminUrl": "/dashboard/admin/logentry",
                    "addUrl": "/dashboard/admin/logentry/add",
                    "perms": {
                        "add": true,
                        "change": true,
                        "delete": true,
                        "view": true
                    },
                    "viewOnly": false
                }
            ]
        },
        ...
    ]
}
```
"""

GET_PERMISSIONS_DOC = """
Returns a list of all permissions.
```json
{
    "permissions": [
        {
            "id": 1,
            "name": "Can add log entry",
            "codename": "add_logentry",
            "contentType": {
                "id": 1,
                "appLabel": "admin",
                "model": "logentry"
            }
        },
        {
            "id": 2,
            "name": "Can change log entry",
            "codename": "change_logentry",
            "contentType": {
                "id": 1,
                "appLabel": "admin",
                "model": "logentry"
            }
        },
        ...
    ]
}
```
"""

GET_CONTENT_TYPES_DOC = """
Returns list of all content types. Content types are matched to permissions.
E.g. add, change, view, delete is assigned to a specific content type:
```json
{
    "contentTypes": [
        {
            "id": 1,
            "appLabel": "admin",
            "model": "logentry"
        },
        {
            "id": 2,
            "appLabel": "auth",
            "model": "permission"
        },
        ...
    ]
}
```
"""

GET_GROUPS_DOC = """
Returns a list of all groups:
```json
{
    "groups": [
        {
            "id": 1,
            "name": "limited",
            "permissions": [
                57,
                36,
                29,
                30,
                31,
                32
            ]
        }
    ]
}
```
"""

GET_LOG_ENTRIES_DOC = """
Returns a list of log entries.
```json
{
    "logEntries": [
        {
            "id": 286,
            "actionTime": "2025-01-09T17:30:10.243340+07:00",
            "objectId": "1",
            "objectRepr": "limited",
            "actionFlag": 2,
            "changeMessage": "[{\"changed\": {\"fields\": [\"Permissions\"]}}]",
            "user": "user_6658ea62-40b4-482a-9b42-f026c4971098",
            "contentType": 3
        },
        {
            "id": 285,
            "actionTime": "2025-01-09T14:21:47.678093+07:00",
            "objectId": "1",
            "objectRepr": "Afghanistan",
            "actionFlag": 3,
            "changeMessage": "",
            "user": "user_6658ea62-40b4-482a-9b42-f026c4971098",
            "contentType": 13
        },
        ...
    ]
}
```
"""

GET_MODEL_RECORD_DOC = """
Returns the model record will data for every field. Returns an error if model is not found
```json
{
    "record": {
        "id": 1,
        "pk": "1",
        "created_at": "2025-01-04T14:05:41.915352+07:00",
        "updated_at": "2025-01-10T17:45:53.090530+07:00",
        "color": "Red",
        "name": "Duck Tales-55",
        "email": "voltron@mail.com",
        "ordering": 1,
        "range_number": 6,
        "amount": "0.00",
        "comment": "this is a comment",
        "is_active": true,
        "date": "2024-10-04",
        "time": "14:59:38",
        "last_log": "2024-12-26T11:55:00+07:00",
        "file": "/media/Screenshot_2024-12-20_at_2.04.06_PM.png",
        "image": "/media/alexa.png",
        "metadata": "{\"job\":\"IT\",\"age\":23,\"name\":\"Mike\"}",
        "html": "<h1>alert(\"Hello\")</h1>",
        "type": 3,
        "classification": [
            {
                "pk": 3,
                "string_value": "Omnivore"
            }
        ],
        "permissions": [
            {
                "pk": 1,
                "string_value": "Administration | log entry | Can add log entry"
            },
            {
                "pk": 2,
                "string_value": "Administration | log entry | Can change log entry"
            }
        ]
    }
}
```
"""

CHANGE_MODEL_RECORD_DOC = """
Updates the model record. Accepts the fields of the model record for POST body.
Returns on successful change.
```json
{
    "message": "Updated record <record string> with pk <pk> successfully"
}
```
"""

ADD_MODEL_RECORD_DOC = """
Createss a new model record. Accepts the fields of the model record for POST body.
Returns on successful change.
```json
{
    "message": "Created record <record string> with pk <pk> successfully"
}
```
"""

ADD_CHANGE_MODEL_RECORD_ERROR_DOC = """
Returned on validation error
```json
{
        'message': 'Invalid data',
        'validation_error': {
            '<fieldname>': '<error message>',
            ...
        }
    }
```
For other errors:
```json
{
    'message': 'Something went wrong',
    'has_error': True
}
```
"""


DELETE_MODEL_RECORD_DOC = """
Deletes a model record
Returns on successful change.
```json
{
    "message": "Deleted record <record string> with pk <pk> successfully"
}
```
"""

DELETE_MODEL_RECORD_ERROR_DOC = """
Returns when there is an error in deleting a model record
```json
{
    'message': 'Something went wrong',
    'has_error': True
}
```
"""


GET_MODEL_LISTVIEW_DOC = """
Accepts a custom custom_search as a query parameter for search keyword.
Returns a paginated list of records for the model.
```json
{
    "count": 39,
    "next": "http://localhost:8000/api/v1/django-admin/model-listview/demo/demomodel?limit=20&offset=20",
    "previous": null,
    "results": [
        {
            "id": 8,
            "pk": 8,
            "created_at": "2025-01-04T14:06:52.689998+07:00",
            "updated_at": "2025-01-18T10:30:03.871388+07:00",
            "color": "Blue",
            "name": "Captain Caveman-100",
            "email": "gijoe@mail.com",
            "ordering": 90,
            "range_number": 6,
            "amount": "0.00",
            ...
        },
        ...
    ]
}
```
"""

CUSTOM_ACTION_VIEW_DOC = """
For applying custom actions to a set of records for a specific model such as bulk delete.
You need to define your own custom action and response
"""

VERIFY_CLOUDFLARE_TOKEN_DOC = """
Verifies the cloudflare turnstile token. Returns
```json
{
    "isValid": True,
}
```
"""

VERIFY_CLOUDFLARE_TOKEN_ERROR_DOC = """
Verifies the cloudflare turnstile token. Returns
```json
{
    "isValid": False,
}
```
"""

GET_WORKER_QUEUES_DOC = """
Returns a list of all queues with their stats from django-rq. Returns:
```json
{
    "queues": [
        {
            "name": "default",
            "fields": [
                {
                    "label": "Queued Jobs",
                    "value": 0,
                    "field": "jobs"
                },
                {
                    "label": "Oldest Queued Job",
                    "value": "-",
                    "field": "oldest_job_timestamp"
                },
                {
                    "label": "Started Jobs",
                    "value": 0,
                    "field": "started_jobs"
                },
                {
                    "label": "Workers",
                    "value": 2,
                    "field": "workers"
                },
                {
                    "label": "Finished Jobs",
                    "value": 0,
                    "field": "finished_jobs"
                },
                {
                    "label": "Deferred Jobs",
                    "value": 0,
                    "field": "deferred_jobs"
                },
                {
                    "label": "Failed Jobs",
                    "value": 1,
                    "field": "failed_jobs"
                },
                {
                    "label": "Scheduled Jobs",
                    "value": 0,
                    "field": "scheduled_jobs"
                },
                {
                    "label": "Host",
                    "value": "custom_admin_redis",
                    "field": "host"
                },
                {
                    "label": "Port",
                    "value": 6379,
                    "field": "port"
                },
                {
                    "label": "Scheduler PID",
                    "value": null,
                    "field": "scheduler_pid"
                }
            ]
        }
    ]
}
```
"""

GET_FAILED_QUEUED_JOBS_DOC = """
Retrieve a list of failed jobs. Returns:
```json
{
    "failed_jobs": {
        "results": [
            {
                "id": "60d65f0e-a55a-4436-8bd5-86fe451b671d",
                "created_at": "2025-02-03T10:33:23.731922+07:00",
                "started_at": "2025-02-03T10:33:23.917602+07:00",
                "enqueued_at": "2025-02-03T10:33:23.745892+07:00",
                "ended_at": "2025-02-03T10:33:23.934963+07:00",
                "timeout": 360,
                "ttl": null,
                "meta": {},
                "callable": "scripts.queue.func",
                "args": [
                    "FOO"
                ],
                "kwargs": {
                    "bar": "BAZ"
                },
                "execution_info": "Traceback ... Exception: Forced fail\n"
            }
        ],
        "count": 1,
        "table_fields": [
            "id",
            "created_at",
            "enqueued_at",
            "ended_at",
            "callable"
        ]
    }
}
```
"""

GET_QUEUED_JOB_DOC = """
Retrieve the specific queued job. Returns:
```json
{
    "job": {
        "id": "60d65f0e-a55a-4436-8bd5-86fe451b671d",
        "created_at": "2025-02-03T10:33:23.731922+07:00",
        "started_at": "2025-02-03T10:33:23.917602+07:00",
        "enqueued_at": "2025-02-03T10:33:23.745892+07:00",
        "ended_at": "2025-02-03T10:33:23.934963+07:00",
        "timeout": 360,
        "ttl": null,
        "meta": {},
        "callable": "scripts.queue.func",
        "args": [
            "FOO"
        ],
        "kwargs": {
            "bar": "BAZ"
        },
        "execution_info": "Traceback ... Exception: Forced fail\n"
    }
}
```
"""

REQUEUE_FAILED_JOB_DOC = """
Requeues a failed job. Requires the payload
```json
{
    "queue_name": "<string>",
    "job_id": "<string>"
}
```
Returns on success
```json
{
    "success": True,
    "message": "<string>"
}
```
"""


QUERY_BUILDER_DOC = """
Returns the list based on query post data.
{
    "count": 3,
    "fields": [...field names]
    "results": [
        {
            ...fields here
        },
        ...
    ]
}
"""

QUERY_BUILDER_ERROR_DOC = """
On error, returns
{
    "count": 0,
    "fields": []
    "results": [],
    "message": "Invalid data",
    "validation_error": "error_messages"  # when there is a validation error only
}
"""