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
from language2test_api.providers.cloze_question_incorrectly_typed_provider import ClozeQuestionIncorrectlyTypedProvider
from language2test_api.providers.cloze_question_pending_typed_provider import ClozeQuestionPendingTypedProvider
from language2test_api.models.cloze_question_correctly_typed import ClozeQuestionCorrectlyTyped, ClozeQuestionCorrectlyTypedSchema
from language2test_api.models.cloze_question_incorrectly_typed import ClozeQuestionIncorrectlyTyped
from language2test_api.models.cloze_question_pending_typed import ClozeQuestionPendingTyped
from random import randint

from nltk.corpus import wordnet
import nltk
import ssl
from itertools import chain

correctly_typed_provider = ClozeQuestionCorrectlyTypedProvider()
incorrectly_typed_provider = ClozeQuestionIncorrectlyTypedProvider()
pending_typed_provider = ClozeQuestionPendingTypedProvider()

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
            if 'typed' in question:
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


    def delete(self, data, cloze):
        self.__delete_answers_in_typed_lists(cloze)
        for question in cloze.questions:
            for option in question.options:
                db.session.query(ClozeQuestionOption).filter(ClozeQuestionOption.id == option.id).delete()
            db.session.query(ClozeQuestion).filter(ClozeQuestion.id == question.id).delete()
        db.session.query(Cloze).filter(Cloze.name == data.get('name')).delete()


    def __delete_answers_in_typed_lists(self, cloze):
        for question in cloze.questions:
            list = correctly_typed_provider.get_query(question.id)
            for answer in list:
                db.session.query(ClozeQuestionCorrectlyTyped).filter(
                    ClozeQuestionCorrectlyTyped.id == answer.id).delete()

            list = incorrectly_typed_provider.get_query(question.id)
            for answer in list:
                db.session.query(ClozeQuestionIncorrectlyTyped).filter(
                    ClozeQuestionIncorrectlyTyped.id == answer.id).delete()

            list = pending_typed_provider.get_query(question.id)
            for answer in list:
                db.session.query(ClozeQuestionPendingTyped).filter(ClozeQuestionPendingTyped.id == answer.id).delete()
        db.session.commit()

    def update(self, data, cloze):

        data = self.add_category_to_data(data)
        cloze.test_category_id = data.get("test_category_id")
        cloze.text = data.get("text")
        cloze.type = data.get("type")
        cloze.filename = data.get("filename")
        cloze.time_limit = data.get("time_limit")


        list_of_accepted_answers = []
        list_correctly_typed=[]
        list_incorrectly_typed =[]
        list_pending_typed=[]

        # Delete accepted_answers in the cloze_question_correctly_typed
        for question in cloze.questions:
            if type(question.typed) == bool and question.typed:
                list_correctly_typed = correctly_typed_provider.get_query(question.id)
                for answer in list_correctly_typed:
                    db.session.query(ClozeQuestionCorrectlyTyped).filter(ClozeQuestionCorrectlyTyped.id == answer.id).delete()

                list_incorrectly_typed = incorrectly_typed_provider.get_query(question.id)
                for answer in list_incorrectly_typed:
                    db.session.query(ClozeQuestionIncorrectlyTyped).filter(ClozeQuestionIncorrectlyTyped.id == answer.id).delete()

                list_pending_typed = pending_typed_provider.get_query(question.id)
                for answer in list_pending_typed:
                    db.session.query(ClozeQuestionPendingTyped).filter(ClozeQuestionPendingTyped.id == answer.id).delete()

        db.session.commit()

        # Delete questions and options from DB
        for question in cloze.questions:
            for option in question.options:
                db.session.query(ClozeQuestionOption).filter(ClozeQuestionOption.id == option.id).delete()
            db.session.query(ClozeQuestion).filter(ClozeQuestion.id == question.id).delete()

        #Add questions and options to DB
        cloze_questions_oldid_newid = {}
        for index, question_data in enumerate(data.get('questions')):
            # These questions are in the request

            new_id = self.generate_id(field=ClozeQuestion.id)

            if 'id' in question_data and type(question_data['id'])==int:
                previous_id = question_data['id']
                cloze_questions_oldid_newid[previous_id] = new_id

            question_data['id'] = new_id
            question = ClozeQuestion(question_data)

            if 'typed' in question_data and type(question_data['typed']) == bool:
                question.typed = question_data['typed']
            else:
                question.typed = False

            if not question.typed:
                # Add options if question is not typed
                for index_option, option in enumerate(question_data.get('options')):
                    question_option = ClozeQuestionOption(option)
                    question_option.id = self.generate_id(index_option, ClozeQuestionOption.id)
                    question.options.append(question_option)
            else:
                #Add accepted answers to a list (to add them to a database)
                for accepted_answer in question_data.get('accepted_answers'):
                    d = {}
                    d['answer_text'] = accepted_answer['text']
                    d['question_id'] = question.id
                    list_of_accepted_answers.append(d)

            cloze.questions.append(question)

        # Add all accepted answers to db
        for accepted_answer in list_of_accepted_answers:
            correctly_typed_provider.add(accepted_answer['answer_text'], accepted_answer['question_id'])

        #Add pending answers to db
        for pending_word in list_pending_typed:
            if pending_word.cloze_question_id in cloze_questions_oldid_newid:
                new_id = cloze_questions_oldid_newid[pending_word.cloze_question_id]
                pending_typed_provider.add(pending_word.text, new_id)

        #Add incorrect answers to db
        for incorrect_word in list_incorrectly_typed:
            if incorrect_word.cloze_question_id in cloze_questions_oldid_newid:
                new_id = cloze_questions_oldid_newid[incorrect_word.cloze_question_id]
                incorrectly_typed_provider.add(incorrect_word.text, new_id)

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
        #nltk.download("wordnet")
