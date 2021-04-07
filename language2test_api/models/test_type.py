from language2test_api.models.base_model import BaseModel, BaseModelSchema

class TestType(BaseModel):
    __tablename__ = 'test_type'

    def __init__(self, item):
        BaseModel.__init__(self, item)

    def __repr__(self):
        return '<test_type %r>' % self.name

class TestTypeSchema(BaseModelSchema):
    class Meta:
        model = TestType

