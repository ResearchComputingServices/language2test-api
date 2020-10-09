import re
import random
from flask import request
from flask import json, Response
from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.cloze import Cloze, ClozeSchema
from language2test_api.models.cloze_question import ClozeQuestion, ClozeQuestionSchema
from language2test_api.models.cloze_question_option import ClozeQuestionOption, ClozeQuestionOptionSchema
from language2test_api.providers.cloze_question_correctly_typed_provider import ClozeQuestionCorrectlyTypedProvider
from random import randint

from nltk.corpus import wordnet
import nltk
import ssl
from itertools import chain

correctly_typed_provider = ClozeQuestionCorrectlyTypedProvider()

class ClozeProvider(BaseProvider):
    def get_count(self, field, cloze_question_id=None):
        query = db.session.query(field.id)
        if cloze_question_id is not None:
            query = query.filter_by(cloze_question_id=cloze_question_id)
        count = query.count()
        dict = {"count": count}
        response = Response(json.dumps(dict), 200, mimetype="application/json")
        return response

    def query_all(self, field, cloze_question_id=None):
        query = field.query
        if cloze_question_id is not None:
            query = query.filter_by(cloze_question_id=cloze_question_id)
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        result = query.all()
        return result

    def add(self, data):
        data['id'] = self.generate_id(field=Cloze.id)
        data = self.add_category_to_data(data)
        cloze = Cloze(data)
        offset = 0

        for index, question in enumerate(data.get('questions')):
            question['id'] = self.generate_id(index, ClozeQuestion.id)
            cloze_question = ClozeQuestion(question)

            #The cloze question is not typed.
            if not type(cloze_question.typed) or not cloze_question.typed:
                for index_option, option in enumerate(question.get('options')):
                    cloze_question_option = ClozeQuestionOption(option)
                    cloze_question_option.id = self.generate_id(index_option + offset, ClozeQuestionOption.id)
                    cloze_question.options.append(cloze_question_option)

                offset = offset + index_option + 1
            cloze.questions.append(cloze_question)
        db.session.add(cloze)
        db.session.commit()
        self.__add_correctly_typed_answers(data)
        return cloze

    def __add_correctly_typed_answers(self, data):
        for question in (data.get('questions')):
            if type(question['typed'])==bool and question['typed']:
                for accepted_answer in question.get('accepted_answers'):
                   if 'text' in accepted_answer:
                        correctly_typed_provider.add(accepted_answer['text'], question['id'])
        return

    def get_correctly_typed_answers_all_clozes(self, data):
        for cloze in data:
            self.get_correctly_typed_answers(cloze)
        return data

    def get_correctly_typed_answers(self, cloze):
        for question in cloze['questions']:
            question['accepted_answers'] = []
            if question['typed']:
                accepted_answers_list = correctly_typed_provider.get_query(question['id'])
                temp = []
                for accepted_answer in accepted_answers_list:
                    d = {}
                    d['text'] = accepted_answer.text
                    temp.append(d)
                question['accepted_answers'] = temp
        return cloze


    def add_original(self, data):
        data['id'] = self.generate_id(field=Cloze.id)
        data = self.add_category_to_data(data)
        cloze = Cloze(data)
        offset = 0

        for index, question in enumerate(data.get('questions')):
            question['id'] = self.generate_id(index, ClozeQuestion.id)
            cloze_question = ClozeQuestion(question)

            for index_option, option in enumerate(question.get('options')):
                cloze_question_option = ClozeQuestionOption(option)
                cloze_question_option.id = self.generate_id(index_option + offset, ClozeQuestionOption.id)
                cloze_question.options.append(cloze_question_option)

            offset = offset + index_option + 1
            cloze.questions.append(cloze_question)

        db.session.add(cloze)
        return cloze



    def delete(self, data, cloze):
        for question in cloze.questions:
            for option in question.options:
                db.session.query(ClozeQuestionOption).filter(ClozeQuestionOption.id == option.id).delete()
            db.session.query(ClozeQuestion).filter(ClozeQuestion.id == question.id).delete()
        db.session.query(Cloze).filter(Cloze.name == data.get('name')).delete()

    def update(self, data, cloze):
        data = self.add_category_to_data(data)
        cloze.test_category_id = data.get("test_category_id")
        cloze.text = data.get("text")
        cloze.type = data.get("type")
        cloze.filename = data.get("filename")
        cloze.time_limit = data.get("time_limit")
        cloze.questions = []

        for index, question in enumerate(data.get('questions')):
            question['id'] = self.generate_id(field=ClozeQuestion.id)
            cloze_question = ClozeQuestion(question)
            for index_option, option in enumerate(question.get('options')):
                cloze_question_option = ClozeQuestionOption(option)
                cloze_question_option.id = self.generate_id(index_option, ClozeQuestionOption.id)
                cloze_question.options.append(cloze_question_option)
            cloze.questions.append(cloze_question)

        db.session.commit()
        return cloze

    @staticmethod
    def generate_options(word, full_text, index):
        hint = False
        previous_letter = full_text[index - len(word) - 2] or ''
        has_previous_letter = previous_letter != ' ' and previous_letter != '' and previous_letter != '*'
        if has_previous_letter:
            word = previous_letter + word
            hint = True
        new_word = word.replace('<typed/>', '')
        typed = len(word) != len(new_word)
        option_bracket_open = False
        option_segment = ''
        segment = ''
        for i in range(len(new_word)):
            letter = new_word[i]
            if letter == '<':
                option_bracket_open = True
                continue
            if letter == '>':
                option_bracket_open = False
                continue
            if option_bracket_open:
                option_segment += letter;
            elif (word != '<' and word != '>'):
                segment += letter
        options = option_segment.split(',')
        options = [{ 'text': x } for x in options if x]
        options = [{ 'text': segment }] + options;
        return segment, typed, options, 1, hint

    @staticmethod
    def generate_questions(text):
        words = []
        if text:
            segment = ''
            bracket_open = False
            for i in range(len(text)):
                word = text[i]
                if word == '*' and not bracket_open:
                    segment = ''
                    bracket_open = True
                elif word == '*' and bracket_open:
                    word, typed, options, correct, hint = ClozeProvider.generate_options(segment, text, i)
                    if typed:
                        words.append({
                            'text': word,
                            'typed': typed,
                            'hint': hint,
                            'accepted_answers': options,
                        })
                    else:
                        words.append({
                            'text': word,
                            'typed': typed,
                            'options': options,
                            'correct': correct,
                        })
                    segment = ''
                    bracket_open = False
                else:
                    segment += word
        return words

    @staticmethod
    def download_wordnet():
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        nltk.download("wordnet")
