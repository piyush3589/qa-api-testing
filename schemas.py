"""JSON Schemas used to validate API responses (contract testing)."""

POST_SCHEMA = {
    "type": "object",
    "required": ["userId", "id", "title", "body"],
    "properties": {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string", "minLength": 1},
        "body": {"type": "string"},
    },
}

COMMENT_SCHEMA = {
    "type": "object",
    "required": ["postId", "id", "name", "email", "body"],
    "properties": {
        "postId": {"type": "integer"},
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "pattern": r"^[^@\s]+@[^@\s]+\.[^@\s]+$"},
        "body": {"type": "string"},
    },
}

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "username", "email", "address", "phone", "website", "company"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "email": {"type": "string", "pattern": r"^[^@\s]+@[^@\s]+\.[^@\s]+$"},
        "address": {
            "type": "object",
            "required": ["street", "suite", "city", "zipcode", "geo"],
        },
        "phone": {"type": "string"},
        "website": {"type": "string"},
        "company": {"type": "object", "required": ["name"]},
    },
}
