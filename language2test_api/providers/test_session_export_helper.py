from typing import List
class TestSessionExportHelper:
    def from_dict(keys: list):
        def _(d: dict):
            result = dict.fromkeys(keys)
            for k in keys:
                result[k] = d.get(k)

            return result

        return _

    def dicts2str(dicts: List[dict], key: str) -> str:
        return ", ".join(map(lambda e: e.get(key, ""), dicts))

    def extract_info(keys: list, d: dict):
        infos = list(map(TestSessionExportHelper.from_dict(keys), d))
        for info in infos:
            options = list(map(lambda e: e.get("text", ""), info["options"]))
            keys = list(map(lambda i: "option {}".format(i), range(1, len(options) + 1)))
            options = zip(keys, options)
            info.pop("options")
            info.update(options)
        return infos

    def update_answers(infos: List[dict], answers, correct_answers):
        for i, info in enumerate(infos):
            if i > len(answers) - 1:
                info["answer"] = None
                info["correct_answer"] = None
                info["result"] = "Empty answer"
            else:
                info["answer"] = answers[i]
                info["correct_answer"] = correct_answers[i]
                info["result"] = "Correct" if answers[i] == correct_answers[i] else "Incorrect"

    def calculate_time_consumption(end_time, start_time):
        if (end_time is None) or (start_time is None):
            test_time = "N/A"
        else:
            hour = int(end_time[11:13]) - int(start_time[11:13])
            minute = int(end_time[14:16]) - int(start_time[14:16])
            second = int(end_time[17:19]) - int(start_time[17:19])
            if second < 0:
                second = second + 60
                minute = minute - 1
            if minute < 0:
                minute = minute + 60
                hour = hour -1
            if hour < 0:
                hour = hour + 24
            test_time = str(hour) + 'hour(s) ' + str(minute) + 'minute(s) ' + str(second) + 'second(s)'
        return test_time

    def grade_calculator(grade, total):
        if grade is None:
            grade = 0;
        if total is None:
            total = 0;
        total_score = "{}/{}".format(grade, total)
        return total_score

    def calculate_correctly_answered_questions(answers):
        num_correctly = 0
        for answer in answers:
            if answer['answered_correctly'] == 1:
                num_correctly += 1
        return num_correctly

    def calculate_correctly_answered_questions_writings(answers):
        num_correctly = 0
        for answer in answers:
            if answer['answer']['answered_correctly'] == 1:
                num_correctly += 1
        return num_correctly

