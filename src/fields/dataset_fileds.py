from flask_restful import fields

from fields.base import DateTimeField

dataset_fields = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'account_id': fields.String,
    'created_at': DateTimeField,
    'updated_at': DateTimeField,
    "configs": fields.Raw,
}
