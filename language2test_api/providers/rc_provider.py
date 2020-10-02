from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.rc import RC, RCSchema
from language2test_api.models.rc_question import RCQuestion, RCQuestionSchema
from language2test_api.models.rc_question_option import RCQuestionOption, RCQuestionOptionSchema
from language2test_api.providers.test_provider import TestProvider
import re


class RCProvider(BaseProvider):
    def add(self, data):
        data['id'] = self.generate_id(field=RC.id)
        data = self.add_category_to_data(data)
        rc = RC(data)
        offset = 0

        for index, question in enumerate(data.get('questions')):
            question['id'] = self.generate_id(index, RCQuestion.id)
            rc_question = RCQuestion(question)

            for index_option, option in enumerate(question.get('options')):
                rc_question_option = RCQuestionOption(option)
                rc_question_option.id = self.generate_id(index_option+offset, RCQuestionOption.id)
                rc_question.options.append(rc_question_option)

            offset = offset + index_option + 1
            rc.questions.append(rc_question)

        db.session.add(rc)
        return rc

    def delete(self, data, rc):
        for question in rc.questions:
            for option in question.options:
                db.session.query(RCQuestionOption).filter(RCQuestionOption.id == option.id).delete()
            db.session.query(RCQuestion).filter(RCQuestion.id == question.id).delete()
        db.session.query(RC).filter(RC.name == data.get('name')).delete()


    def update(self, data, rc):
        data = self.add_category_to_data(data)
        rc.test_category_id = data.get("test_category_id")
        rc.text = data.get("text")
        rc.type = data.get("type")
        rc.filename = data.get("filename")
        rc.time_limit = data.get("time_limit")

        #Deleting the questions causes exception when there are links to other tables
        #for question in rc.questions:
        #    for option in question.options:
        #        db.session.query(RCQuestionOption).filter(RCQuestionOption.id == option.id).delete()
        #    db.session.query(RCQuestion).filter(RCQuestion.id == question.id).delete()

        #Putting questions to null causes ghosts rows in linked tables (i.e. test sessions)
        rc.questions = []
        for index, question in enumerate(data.get('questions')):
            question['id'] = self.generate_id(field=RCQuestion.id)

            rc_question = RCQuestion(question)
            for index_option, option in enumerate(question.get('options')):
                rc_question_option = RCQuestionOption(option)
                rc_question_option.id = self.generate_id(index_option, RCQuestionOption.id)
                rc_question.options.append(rc_question_option)

            rc.questions.append(rc_question)
        db.session.commit()
        return rc



    @staticmethod
    def gen_question(question_text):
        res = {}
        text = question_text.strip().split("\n")
        res["question"] = text[0].strip()
        res["options"] = list(map(lambda x: re.findall(r"\s(.*)", x)[0].strip(), text[1:5]))
        res["correct"] = ["A", "B", "C", "D"].index(re.findall(r"\s(.*)", text[5])[0].strip()) + 1
        return res