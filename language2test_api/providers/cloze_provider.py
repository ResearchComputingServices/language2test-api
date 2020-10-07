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


        #for question in cloze.questions:
        #    for option in question.options:
        #        db.session.query(ClozeQuestionOption).filter(ClozeQuestionOption.id == option.id).delete()
        #    db.session.query(ClozeQuestion).filter(ClozeQuestion.id == question.id).delete()

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
    def generate_options(word):
        options = []
        for syn in wordnet.synsets(word): 
            for l in syn.lemmas(): 
                options.append(l.name()) 
                if l.antonyms(): 
                    options.append(l.antonyms()[0].name())
        return set(options)

    @staticmethod
    def generate_cloze_question_options(word, previous_letter = ''):
        word = word.strip(',.-\n')
        options = []
        synonyms = wordnet.synsets(word)
        previous_letter = previous_letter.strip(',.-\n')
        has_previous_letter = previous_letter != ' ' and previous_letter != ''
        lemmas = ClozeProvider.generate_options(word)
        if word in lemmas:
            lemmas.remove(word)
        options.extend(lemmas)
        if has_previous_letter:
            def filter_options(option):
                return option[0] == previous_letter
            options = filter(filter_options, options)
        mapped_options = []
        for option in options:
            option = ' '.join(option.split('_'))
            mapped_options.append({ 'text': option })
        random_correct = randint(0, len(mapped_options))
        mapped_options.insert(random_correct, { 'text': word })
        return mapped_options, random_correct + 1

    @staticmethod
    def generate_questions(text, typed = False):
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
                    # We take into consideration about the fact that, words can be a<pple> words can be sliced up.
                    previous_letter = text[i - len(segment) - 2]
                    has_previous_letter = previous_letter != ' ' and previous_letter != '' and previous_letter != '*'
                    if has_previous_letter:
                        segment = previous_letter + segment
                    if not typed:
                        options, random_correct = ClozeProvider.generate_cloze_question_options(segment, previous_letter)
                        words.append({
                            'text': segment,
                            'options': options,
                            'correct': random_correct,
                            'typed': typed
                        })
                    else:
                        words.append({
                            'text': segment,
                            'accepted_answers': [{ 'text': segment }],
                            'typed': typed
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
