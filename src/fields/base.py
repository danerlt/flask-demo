from flask_restful import fields


class TimestampField(fields.Raw):
    def format(self, value):
        return int(value.timestamp())


class DateTimeField(fields.Raw):
    def format(self, value):
        return value.strftime("%Y-%m-%d %H:%M:%S")