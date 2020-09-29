from sqlalchemy.sql import text
from flask import json, jsonify, Response, blueprints, request
from language2test_api.extensions import db, ma
from collections import namedtuple
from language2test_api.providers.raw_sql_provider import RawSqlProvider
from language2test_api.providers.test_session_export_helper import TestSessionExportHelper as testhelper
from typing import List
import pandas as pd
from io import BytesIO
from docx import Document
import zipfile

class TestSessionExportProvider(RawSqlProvider):
    def write_results_into_file(self, results, name):
        
        test_time = testhelper.calculate_time_consumption(results['end_datetime'], results['start_datetime'])

        basic_info= {
            "User ID": results['user_id'],
            "Test Info": results['name'],
            "User Name": results['user']['name'],
            "First Name": results['user']['first_name'],
            "Last Name": results['user']['last_name'],
            "Start Time": results['start_datetime'],
            "End Time": results['end_datetime'],
            "Time Consumption": test_time
        }


        if ('results_vocabulary' in results) and ((len(results['results_vocabulary'])) > 0):
            voc_score = testhelper.calculate_correctly_answered_questions(results['results_vocabulary'][0]['answers'])
            voc_total = len(results['results_vocabulary'][0]['answers'])
            voc_grade = testhelper.grade_calculator(voc_score, voc_total)
            if voc_total > 0:
                basic_info["Vocabulary Grade"]= voc_grade


        if 'results_rc' in results and ((len(results['results_rc'])) > 0):
            rc_score = testhelper.calculate_correctly_answered_questions(results['results_rc'][0]['answers'])
            rc_total = len(results['results_rc'][0]['answers'])
            rc_grade = testhelper.grade_calculator(rc_score, rc_total)
            if rc_total > 0:
                basic_info["Reading Comprehension Grade"]= rc_grade

        if 'results_cloze' in results and ((len(results['results_cloze'])) > 0):
            cloze_score = testhelper.calculate_correctly_answered_questions(results['results_cloze'][0]['answers'])
            cloze_total = len(results['results_cloze'][0]['answers'])
            cloze_grade = testhelper.grade_calculator(cloze_score, cloze_total)
            if cloze_total > 0:
                basic_info["Cloze Grade"] = cloze_grade

        if 'results_writing' in results and ((len(results['results_writing'])) > 0):
            writing_score = testhelper.calculate_correctly_answered_questions_writings(results['results_writing'])
            writing_total = len(results['results_writing'])
            writing_grade = testhelper.grade_calculator(writing_score, writing_total)
            if writing_total > 0:
                basic_info["Writing Grade"] = writing_grade

        test_results = results['test']

        if ('test_vocabulary' in test_results) and (len(test_results['test_vocabulary']) > 0):
            voc_results = test_results["test_vocabulary"]
            voc_infos = []
            for i in range(len(results['results_vocabulary'][0]['answers'])):
                answer = results['results_vocabulary'][0]['answers'][i]['text']
                if answer is None:
                    test_result = "Empty Answer"
                elif answer == voc_results[i]['options'][int(voc_results[i]['correct'])-1]['text']:
                    test_result = "Correct"
                else:
                    test_result = "Incorrect"
                test_voc_time = testhelper.calculate_time_consumption(results['results_vocabulary'][0]['answers'][i]['end_time'],
                                                                      results['results_vocabulary'][0]['answers'][i]['start_time'])
                voc_infos.append({
                    "Vocabulary": str(i+1),
                    "Test Type": voc_results[i]['type'],
                    "Word": voc_results[i]['word'],
                    "Option 1": voc_results[i]['options'][0]['text'],
                    "Option 2": voc_results[i]['options'][1]['text'],
                    "Option 3": voc_results[i]['options'][2]['text'],
                    "Option 4": voc_results[i]['options'][3]['text'],
                    "Student Answer": answer,
                    "Correct Answer": voc_results[i]['options'][int(voc_results[i]['correct'])-1]['text'],
                    "Difficulty": voc_results[i]['difficulty'],
                    "Test Result": test_result,
                    "Time Consumption": test_voc_time
                })

        if 'test_rc' in test_results and (len(test_results['test_rc']) > 0):
            rc_results = test_results["test_rc"]
            rc_infos = []
            for i in range(len(rc_results)):
                rc_questions = test_results["test_rc"][i]['questions']
                for j in range(len(rc_questions)):
                    answer = results['results_rc'][i]['answers'][j]['text']
                    if answer is None:
                        test_result = "Empty Answer"
                    elif answer == rc_questions[j]['options'][int(rc_questions[j]['correct'])-1]['text']:
                        test_result = "Correct"
                    else:
                        test_result = "Incorrect"
                    test_rc_time = testhelper.calculate_time_consumption(
                        results['results_rc'][i]['answers'][j]['end_time'],
                        results['results_rc'][i]['answers'][j]['start_time'])
                    rc_infos.append({
                        "RC": str(j+1),
                        "Question": rc_questions[j]['text'],
                        "Option 1": rc_questions[j]['options'][0]['text'],
                        "Option 2": rc_questions[j]['options'][1]['text'],
                        "Option 3": rc_questions[j]['options'][2]['text'],
                        "Option 4": rc_questions[j]['options'][3]['text'],
                        "User Answer": results['results_rc'][i]['answers'][j]['text'],
                        "Correct Answer": rc_questions[j]['options'][int(rc_questions[j]['correct'])-1]['text'],
                        "Test Result": test_result,
                        "Time Consumption":test_rc_time
                    })


        if 'test_cloze' in test_results  and (len(test_results['test_cloze']) > 0):
            cloze_results = test_results["test_cloze"]
            print(cloze_results)
            cloze_infos =[]
            for i in range(len(cloze_results)):
                cloze_questions = test_results["test_cloze"][i]['questions']
                for j in range(len(cloze_questions)):
                    answer = results['results_cloze'][i]['answers'][j]['text']
                    if answer is None:
                        test_result = "Empty Answer"
                    elif answer == cloze_questions[j]['options'][int(cloze_questions[j]['correct'])-1]['text']:
                        test_result = "Correct"
                    else:
                        test_result = "Incorrect"
                    test_cloze_time = testhelper.calculate_time_consumption(
                        results['results_cloze'][i]['answers'][j]['end_time'],
                        results['results_cloze'][i]['answers'][j]['start_time'])
                    cloze_infos.append({
                        "Question": cloze_questions[j]['text'],
                        "Option 1": cloze_questions[j]['options'][0]['text'],
                        "Option 2": cloze_questions[j]['options'][1]['text'],
                        "Option 3": cloze_questions[j]['options'][2]['text'],
                        "Option 4": cloze_questions[j]['options'][3]['text'],
                        "User Answer": results['results_cloze'][i]['answers'][j]['text'],
                        "Correct Answer": cloze_questions[j]['options'][int(cloze_questions[j]['correct'])-1]['text'],
                        "Test Result": test_result,
                        "Time Consumption": test_cloze_time
                    })

        if 'test_writing' in test_results and (len(test_results['test_writing']) > 0):
            writing_results = test_results["test_writing"]
            writing_infos =[]
            for i in range(len(writing_results)):
                test_writing_time = testhelper.calculate_time_consumption(
                    results['results_writing'][i]['answer']['end_time'],
                    results['results_writing'][i]['answer']['start_time'])
                writing_infos.append({
                    "Writing": str(i+1),
                    "Test name": writing_results[i]['name'],
                    "Question": writing_results[i]['question'],
                    "Word Limit": writing_results[i]['word_limit'],
                    "Time Limit": writing_results[i]['time_limit'],
                    "Essay": results['results_writing'][i]['answer']['text'],
                    "Time Consumption": test_writing_time
                })

        xlsx = BytesIO()
        with pd.ExcelWriter(xlsx, engine='xlsxwriter') as writer:
            pd.DataFrame([basic_info]).to_excel(writer, sheet_name="Basic info", index=False)
            workbook = writer.book
            worksheet = writer.sheets["Basic info"]
            format = workbook.add_format()
            format.set_align('center')
            format.set_align('vcenter')

            worksheet.set_column('A:C', 15, format)
            worksheet.set_column('B:B', 45, format)
            worksheet.set_column('D:D', 30, format)
            worksheet.set_column('E:E', 15, format)
            worksheet.set_column('F:G', 25, format)
            worksheet.set_column('H:H', 40, format)
            worksheet.set_column('I:L', 25, format)

            if ('results_vocabulary' in results) and ((len(results['results_vocabulary'])) > 0):
                if voc_total > 0:
                    pd.DataFrame(voc_infos).to_excel(writer, sheet_name="Vocabulary Test Info", index=False)
                    pd.DataFrame([voc_grade], index=["Grade"]).to_excel(writer, startrow=1 + len(voc_infos),
                                                                        sheet_name="Vocabulary Test Info",
                                                                        header=False)
                    workbook = writer.book
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet = writer.sheets["Vocabulary Test Info"]
                    worksheet.set_column('A:A', 13, format)
                    worksheet.set_column('B:B', 16, format)
                    worksheet.set_column('C:C', 18, format)
                    worksheet.set_column('D:D', 16, format)
                    worksheet.set_column('E:E', 16, format)
                    worksheet.set_column('F:I', 16, format)
                    worksheet.set_column('J:K', 20, format)
                    worksheet.set_column('L:L', 28, format)

            if ("results_rc" in results) and ((len(results['results_rc'])) > 0):
                if rc_total > 0:
                    pd.DataFrame(rc_infos).to_excel(writer, sheet_name="Reading Comprehension Test Info", index=False)
                    pd.DataFrame([rc_grade], index=["Grade"]).to_excel(writer, startrow=1 + len(rc_infos),
                                                                       sheet_name="Reading Comprehension Test Info",
                                                                       header=False)
                    workbook = writer.book
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet = writer.sheets["Reading Comprehension Test Info"]
                    worksheet.set_column('A:A', 15, format)
                    worksheet.set_column('B:H', 60, format)
                    worksheet.set_column('I:I', 25, format)
                    worksheet.set_column('J:J', 28, format)

            if ("results_cloze" in results) and ((len(results['results_cloze'])) > 0):
                if cloze_total > 0:
                    pd.DataFrame(cloze_infos).to_excel(writer, sheet_name="Cloze Test Info", index=False)
                    pd.DataFrame([cloze_grade], index=["Grade"]).to_excel(writer, startrow=1 + len(cloze_infos),
                                                                          sheet_name="Cloze Test Info",
                                                                          header=False)
                    workbook = writer.book
                    worksheet = writer.sheets["Cloze Test Info"]
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet.set_column('A:A', 13, format)
                    worksheet.set_column('B:B', 16, format)
                    worksheet.set_column('C:I', 28, format)

            if ('results_writing' in results) and ((len(results['results_writing'])) > 0):
                if writing_total >0:
                    pd.DataFrame(writing_infos).to_excel(writer, sheet_name="Writing Test Info", index=False)
                    pd.DataFrame([writing_grade], index=["Grade"]).to_excel(writer, startrow=1 + len(writing_infos),
                                                                            sheet_name="Writing Test Info",
                                                                            header=False)
                    workbook = writer.book
                    worksheet = writer.sheets['Writing Test Info']
                    format = workbook.add_format()
                    format.set_align('center')
                    format.set_align('vcenter')
                    worksheet.set_column('A:A', 13, format)
                    worksheet.set_column('B:B', 13, format)
                    worksheet.set_column('C:C', 60, format)
                    worksheet.set_column('D:D', 18, format)
                    worksheet.set_column('E:E', 22, format)
                    worksheet.set_column('F:F', 22, format)
                    worksheet.set_column('G:G', 35, format)
                    writer.save()

        output = BytesIO()
        new_name = name.replace(" - ", " ").replace("-", " ")
        with zipfile.ZipFile(output, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            if ('results_writing' in results) and ((len(results['results_writing'])) > 0):
                for i in range(len(writing_results)):
                    txt = BytesIO()
                    docx = BytesIO()
                    if results['results_writing'][i]['answer']['text'] is None:
                        results['results_writing'][i]['answer']['text'] = " "
                    txt.write((results['results_writing'][i]['answer']['text']).encode("utf8"))
                    document = Document()
                    document.add_paragraph(results['results_writing'][i]['answer']['text'])
                    document.save(docx)
                    file_name = writing_results[i]['name']
                    zip_file.writestr(file_name + ".txt", txt.getvalue())
                    zip_file.writestr(file_name + ".docx", docx.getvalue())
                zip_file.writestr(new_name + ".xlsx", xlsx.getvalue())
            else:
                zip_file.writestr(new_name + ".xlsx", xlsx.getvalue())

        output.seek(0)
        return output

    def test_session_grade_summary(self, results, max_voc_test, max_rc_test, max_cloze_test, max_writing_test):

        test_results = results['test']

        test_infos = {
            "User ID": results['user_id'],
            "Test Info": results['name'],
            "User Name": results['user']['name'],
            "First Name": results['user']['first_name'],
            "Last Name": results['user']['last_name']
        }
        if max_voc_test > 0:
            if ('test_vocabulary' in test_results) and (len(test_results['test_vocabulary']) > 0):
                voc_results = test_results["test_vocabulary"]
                for i in range(len(results['results_vocabulary'][0]['answers'])):

                    answer = results['results_vocabulary'][0]['answers'][i]['text']

                    if answer is None:
                        test_result = " "
                    elif answer == voc_results[i]['options'][int(voc_results[i]['correct'])-1]['text']:
                        test_result = 1
                    else:
                        test_result = 0

                    test_infos["voc #" + str(i+1)] = test_result

                    if len(results['results_vocabulary'][0]['answers']) < max_voc_test:
                        missing_num_voc = max_voc_test - len(results['results_vocabulary'][0]['answers'])
                        for j in range(missing_num_voc):
                            test_infos["voc #" + str(i + j + 1)] = 0

            else:
                for k in range(max_voc_test):
                    test_infos["voc #" + str(k + 1)]: ""

        if max_rc_test > 0:
            rc_results = test_results["test_rc"]

            if 'test_rc' in test_results and (len(test_results['test_rc']) > 0):

                for i in range(len(rc_results)):
                    rc_questions = test_results["test_rc"][i]['questions']
                    for j in range(len(rc_questions)):
                        answer = results['results_rc'][i]['answers'][j]['text']
                        if answer is None:
                            answer = ""
                        if answer == "":
                            test_result = " "
                        elif answer == rc_questions[j]['options'][int(rc_questions[j]['correct']) - 1]['text']:
                            test_result = 1
                        else:
                            test_result = 0
                        test_infos["rc #" + str(i + 1) + " q #" + str(j + 1)] = test_result

                        if len(test_results["test_rc"][i]['questions']) < max_rc_test:
                            missing_num_rc = max_rc_test - len(test_results["test_rc"][i]['questions'])
                            for k in range(missing_num_rc):
                                test_infos["rc #" + str(j + k + 1)]: " "

            else:
                for h in range(max_rc_test):
                    test_infos["rc #" + str(h + 1)]: ""

        if max_cloze_test > 0:
            if 'test_cloze' in test_results and (len(test_results['test_cloze']) > 0):
                cloze_results = test_results["test_cloze"]
                print(cloze_results)
                for i in range(len(cloze_results)):
                    cloze_questions = test_results["test_cloze"][i]['questions']
                    for j in range(len(cloze_questions)):
                        answer = results['results_cloze'][i]['answers'][j]['text']
                        if answer is None:
                            test_result = " "
                        elif answer == cloze_questions[j]['options'][int(cloze_questions[j]['correct']) - 1]['text']:
                            test_result = 1
                        else:
                            test_result = 0
                        test_infos["cloze #" + str(i + 1) + " q #" + str(j + 1)] = test_result

                        if len(cloze_questions) < max_cloze_test:
                            missing_num_cloze = max_cloze_test - len(cloze_questions)
                            for k in range(missing_num_cloze):
                                test_infos["cloze #" + str(j + k + 1)]: " "
            else:
                for h in range(max_cloze_test):
                    test_infos["cloze #" + str(h + 1)]: ""

        if max_writing_test > 0:
            if 'test_writing' in test_results and (len(test_results['test_writing']) > 0):
                writing_results = test_results["test_writing"]
                for i in range(max_writing_test):
                    test_infos["writing # " + str(i + 1)] = 0

                    if len(writing_results) < max_writing_test:
                        missing_num_writing = max_writing_test - len(writing_results)
                        for j in range(missing_num_writing):
                            test_infos["writing # " + str(j + 1)] = " "
            else:
                for h in range(max_cloze_test):
                    test_infos["writing # " + str(h + 1)] = " "

        return test_infos
