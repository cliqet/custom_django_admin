GET_ALL_QUERY_BUILDERS_DOC = """
Gets a list of all query builders saved
```json
{
    "queries": [
        {
            "id": 1,
            "name": "Is Active Demo Models",
            "query": {
                "app_name": "demo",
                "model_name": "DemoModel",
                "conditions": [
                    [
                        "is_active",
                        "equals",
                        "True"
                    ]
                ],
                "orderings": [
                    "ordering"
                ],
                "query_limit": null
            }
        },
        ...
    ]
}
```
"""

ADD_QUERY_BUILDER_DOC = """
Save query from a query builder. Returns:
```json
{
    "message": "Successfully added query <query name>"
}
```
"""

CHANGE_QUERY_BUILDER_DOC = """
Save query from a query builder. Returns:
```json
{
    "message": "Successfully changed query with id <id>"
}
```
"""

DELETE_QUERY_BUILDER_DOC = """
Save query from a query builder. Returns:
```json
{
    "message": "Successfully deleted query with id <id>"
}
```
"""