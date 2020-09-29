import re
import random
from flask import request
from flask import json, Response
from language2test_api.extensions import db, ma
from language2test_api.providers.base_provider import BaseProvider
from language2test_api.models.cloze import Cloze, ClozeSchema
from language2test_api.models.cloze_question import ClozeQuestion, ClozeQuestionSchema
from language2test_api.models.cloze_question_option import ClozeQuestionOption, ClozeQuestionOptionSchema
from random import randint

from nltk.corpus import wordnet
import nltk
import ssl
from itertools import chain

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


        for question in cloze.questions:
            for option in question.options:
                db.session.query(ClozeQuestionOption).filter(ClozeQuestionOption.id == option.id).delete()
            db.session.query(ClozeQuestion).filter(ClozeQuestion.id == question.id).delete()


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
    def generate_questions(text, typed = False):
        words = []
        if text:
            start_index = 0
            segment = ''
            bracket_open = False
            for i in range(len(text)):
                word = text[i]
                if word == '*' and not bracket_open:
                    segment = ''
                    bracket_open = True
                elif word == '*' and bracket_open:
                    # We take into consideration about the fact that, words can be a<pple> words can be sliced up.
                    previous_word = text[i - len(segment) - 2]
                    options = []
                    if previous_word != ' ' and previous_word != '':
                        segment = previous_word + segment
                        synonyms = wordnet.synsets(segment)
                        lemmas = set(chain.from_iterable([segment.lemma_names() for segment in synonyms]))
                        if segment in lemmas:
                            lemmas.remove(segment)
                        lemmas = list(lemmas)
                        if len(lemmas) >= 3:
                            options.extend(lemmas[:3])
                        else:
                            options.extend(lemmas)
                        def filter_options(option):
                            return option[0] == previous_word
                        options = filter(filter_options, options)
                    mapped_options = []
                    for option in options:
                        option = ' '.join(option.split('_'))
                        mapped_options.append({ 'text': option })
                    random_correct = randint(0, len(mapped_options))
                    mapped_options.insert(random_correct, { 'text': segment })
                    words.append({
                        'word': segment,
                        'options': mapped_options,
                        'correct': random_correct + 1,
                        'start_index': start_index,
                        'end_index': i,
                        'typed': typed
                    })
                    segment = ''
                    bracket_open = False
                else:
                    if segment == '': start_index = i
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

    @staticmethod
    def generate_options(word):
        synonyms = wordnet.synsets(word)
        lemmas = set(chain.from_iterable([word.lemma_names() for word in synonyms]))
        if word in lemmas:
            lemmas.remove(word)
        lemmas = list(lemmas)
        res = []
        if len(lemmas) >= 4:
            res.extend(lemmas[:4])
        else:
            res.extend(lemmas)
            words = ["mark", "synonym", "similar", "same"]
            res.extend(words[:(4 - len(res))])
        return word, res
