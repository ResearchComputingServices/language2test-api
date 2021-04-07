from marshmallow import Schema, fields, ValidationError, pre_load
from sqlalchemy import func, ForeignKey, Sequence, Table, Column, Integer
from sqlalchemy.orm import relationship
from language2test_api.extensions import db, ma
from language2test_api.models.base_text_model import BaseTextModel, BaseTextModelSchema

class VocabularyOption(BaseTextModel):
    __tablename__ = 'vocabulary_option'

    vocabulary_id = Column(db.Integer(), ForeignKey('vocabulary.id'))
    vocabulary = relationship("Vocabulary", back_populates="options")

    def __init__(self, item):
        BaseTextModel.__init__(self, item)
        self.vocabulary_id = item.get('vocabulary_id')

    def __repr__(self):
        return '<vocabulary_option %r>' % self.text

class VocabularyOptionSchema(BaseTextModelSchema):
    class Meta:
        model = VocabularyOption

    vocabulary_id = fields.Integer(dump_only=True)



