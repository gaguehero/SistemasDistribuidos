import datetime as dt

from marshmallow import Schema, fields

class Transaction():
    def __init__(self,description, amout, type):
        self.description = description
        self.amout = amout
        self.created_at = dt.datetime.now()
        self.type = type
    
    def __repr__(self):
        return '<Transaction(name={self.description!r})>'.format(self=self)
        
class TransactionSchema():
    description = fields.Str()
    amount = fields.Number()
    created_at = fields.Date()
    type = fields.Str()