from language2test_api.models.test import Test, TestSchema
from language2test_api.providers.test_provider import TestProvider
from language2test_api.providers.raw_sql_provider import RawSqlProvider
import pandas as pd
from io import BytesIO

test_schema = TestSchema(many=False)
test_schema_many = TestSchema(many=True)
provider = TestProvider()

class TestExportProvider(RawSqlProvider):
    def write_results_into_file(test_id):
        tests = Test.query.filter_by(id=test_id).first()
        result = test_schema.dump(tests)

        demographic_fields_list = []
        for i in range(len(result['test_user_field_category'])):
            demographic_fields_list.append(result['test_user_field_category'][i]['name'])
        mandatory_field_list = []
        for j in range(len(result['mandatory_test_user_field_category'])):
            mandatory_field_list.append(result['mandatory_test_user_field_category'][j]['name'])

        test_infos = {
            "Id": result['id'],
            "name": result['name'],
            "Student Classes": result['test_student_class'][0]['display'],
            "Demographic Fields": ', '.join(demographic_fields_list),
            "Mandatory Demographic Fields": ', '.join(mandatory_field_list)
        }

        if ("test_vocabulary" in result) & (result["test_vocabulary"] != []):
            voc_infos = []
            voc_results = result["test_vocabulary"]
            for voc_result in voc_results:
                option_list = []
                for option in voc_result["options"]:
                    option_list.append(option["text"])
                correct_option=voc_result["correct"]-1
                voc_infos.append({
                    "Word": voc_result["word"],
                    "Options": ", ".join(option_list),
                    "Correct option": voc_result["options"][correct_option]["text"],
                    "Test type": voc_result["type"],
                    "Test category": voc_result["test_category"]["name"],
                    "Test difficulty": voc_result["difficulty"],
                    "Time limit": voc_result["time_limit"]
                })

        if ("test_cloze" in result) & (result["test_cloze"] != []):
            cloze_infos = []
            cloze_results = result["test_cloze"]
            for cloze_result in cloze_results:
                for question in cloze_result["questions"]:
                    option_list = []
                    for q in question["options"]:
                        option_list.append(q["text"])
                    correct_option = question["correct"] - 1
                    cloze_infos.append({
                        "Test name": cloze_result["name"],
                        "Test ID": cloze_result["id"],
                        "Question type": cloze_result["type"],
                        "Question": cloze_result["text"],
                        "Question ID": question["id"],
                        "Options": ", ".join(option_list),
                        "Correct option": question["options"][correct_option]["text"],
                        "Time limit": cloze_result["time_limit"]
                    })

        if ("test_rc" in result) & (result["test_rc"] != []):
            rc_infos = []
            rc_results = result["test_rc"]
            for rc_result in rc_results:
                for question in rc_result["questions"]:
                    option_list = []
                    for q in question["options"]:
                        option_list.append(q["text"])
                    correct_option = question["correct"] - 1
                    rc_infos.append({
                        "Test name": rc_result["name"],
                        "Test ID": rc_result["id"],
                        "Question type": rc_result["type"],
                        "Question": rc_result["text"],
                        "Question ID": question["id"],
                        "Options": ", ".join(option_list),
                        "Correct option": question["options"][correct_option]["text"],
                        "Time limit": rc_result["time_limit"]
                    })

        if ("test_writing" in result) & (result["test_writing"] != []):
            writing_infos = []
            writing_results = result["test_writing"]
            for writing_result in writing_results:
                writing_infos.append({
                    "Test ID": writing_result["id"],
                    "Test name": writing_result["name"],
                    "Question type": writing_result["test_category"]["test_type"]["name"],
                    "Question": writing_result["question"],
                    "Time limit": writing_result["time_limit"]
                })

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame([test_infos]).to_excel(writer, sheet_name="Test Basic info", index=False)
            workbook = writer.book
            format = workbook.add_format()
            format.set_align('center')
            format.set_align('vcenter')
            worksheet = writer.sheets["Test Basic info"]
            worksheet.set_column('A:A', 18, format)
            worksheet.set_column('B:B', 18, format)
            worksheet.set_column('C:C', 25, format)
            worksheet.set_column('D:E', 55, format)

            if ("test_vocabulary" in result) & (result["test_vocabulary"] != []):
                pd.DataFrame(voc_infos).to_excel(writer, sheet_name="Vocabulary test info", index=False)
                workbook = writer.book
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet = writer.sheets["Vocabulary test info"]
                worksheet.set_column('A:C', 18, format)
                worksheet.set_column('B:B', 55, format)
                worksheet.set_column('D:G', 20, format)

            if ("test_cloze" in result) & (result["test_cloze"] != []):
                pd.DataFrame(cloze_infos).to_excel(writer, sheet_name="Cloze test info", index=False)
                workbook = writer.book
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet = writer.sheets["Cloze test info"]
                worksheet.set_column('A:C', 18, format)
                worksheet.set_column('D:D', 30, format)
                worksheet.set_column('E:E', 15, format)
                worksheet.set_column('F:F', 45, format)
                worksheet.set_column('G:H', 18, format)

            if ("test_rc" in result) & (result["test_rc"] != []):
                pd.DataFrame(rc_infos).to_excel(writer, sheet_name="Reading Comprehension test info", index=False)
                workbook = writer.book
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet = writer.sheets["Reading Comprehension test info"]
                worksheet.set_column('A:C', 15, format)
                worksheet.set_column('D:D', 35, format)
                worksheet.set_column('E:E', 15, format)
                worksheet.set_column('F:F', 85, format)
                worksheet.set_column('G:G', 35, format)
                worksheet.set_column('H:H', 18, format)

            if ("test_writing" in result) & (result["test_writing"] != []):
                pd.DataFrame(writing_infos).to_excel(writer, sheet_name="Writing test info", index=False)
                workbook = writer.book
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet = writer.sheets["Writing test info"]
                worksheet.set_column('A:C', 18, format)
                worksheet.set_column('D:D', 65, format)
                worksheet.set_column('E:E', 18, format)

        output.seek(0)
        return output


