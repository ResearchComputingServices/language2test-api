from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.test_category import TestCategory, TestCategorySchema
from language2test_api.models.test_type import TestType, TestTypeSchema

class TestCategoryProvider(BaseProvider):
    def add(self, data):
        data['id'] = self.generate_id(field=TestCategory.id)
        data_test_type = data.get('test_type')
        if data_test_type:
            test_type_name = data_test_type.get('name')
            test_type = TestType.query.filter_by(name=test_type_name).first()
            if test_type:
                data['test_type_id'] = test_type.id
        test_category = TestCategory(data)
        return test_category

    def update(self, data, test_category):
        data_test_type = data.get('test_type')
        if data_test_type:
            test_type_name = data_test_type.get('name')
            test_type = TestType.query.filter_by(name=test_type_name).first()
            if test_type:
                data['test_type_id'] = test_type.id
        test_category.test_type_id = data.get('test_type_id')
        return test_category
