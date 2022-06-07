import glob
import math
import os

import sympy as sp
import pandas as pd

science_group = ["เคมี", "ฟิสิกส์", "ชีว"]


class StudentData:
    def reset(self):
        self.available_period = []
        self.data = {}
        self.unordered_data = []

    def __init__(self):
        self.first_path = os.getcwd()
        self.available_period = []
        self.data = {}
        self.unordered_data = []
        self.all_gpa = {"GPAX": [StudentData.filter_by_subject_number("xxxxxx")],
                        "รายวิชาวิทยาศาสตร์": [StudentData.filter_by_subject_number("วxxxxx")],
                        "รายวิชาสังคมศึกษา": [StudentData.filter_by_subject_number("สxxxxx")],
                        "รายวิชาภาษาไทย": [StudentData.filter_by_subject_number("ทxxxxx")],
                        "รายวิชาคณิตศาสตร์": [StudentData.filter_by_subject_number("คxxxxx")],
                        "รายวิชาการงานอาชีพ": [StudentData.filter_by_subject_number("งxxxxx")],
                        "รายวิชาวิชาคอมพิวเตอร์": [StudentData.filter_by_subject(["โปรเเกรม","โปรแกรม","เทคโนโลยี"])],
                        "รายวิชาภาษาต่างประเทศ": [StudentData.filter_by_subject(["อังกฤษ","พม่า","จีน"])],
                        "ริชาประวัติศาสตร์": [StudentData.filter_by_subject(["ประวัติ"])],
                        "วิชาฟิสิกส์" :[StudentData.filter_by_subject(["ฟิสิกส์"])],
                        "วิชาชีววิทยา": [StudentData.filter_by_subject(["ชีววิทยา"])],
                        "วิชาเคมี": [StudentData.filter_by_subject(["เคมี"])],
                        }

    def add_period(self, file_name, degree, period):
        if degree not in self.data:
            self.data[degree] = {period: self.read_transformed(file_name, degree, period)}
        else:
            self.data[degree][period] = self.read_transformed(file_name, degree, period)

    def read_transformed(self, file_name, degree, period):

        data = pd.read_excel(file_name)
        data = data[["รหัสวิชา", "รายวิชา", "นก.", "เกรด"]]

        data_transformed = []
        for i in data.iloc:
            obj = i.to_dict()
            obj["ปี"] = degree
            obj["ภาคเรียน"] = period
            obj["ภาคเรียนรวมปัจจุบัน"] = ((degree - 1) * 2) + period
            data_transformed.append(obj)
            self.unordered_data.append(obj)

        return data_transformed

    @staticmethod
    def filter_by_subject_number(subjects):
        if not isinstance(subjects, list):
            subjects = [subjects]

        def filter(data):
            for subject in subjects:
                if StudentData.match_number_pattern(subject, data["รหัสวิชา"]):
                    # print(data)
                    return True

        return filter

    @staticmethod
    def match_number_pattern(a, b):
        for a_elem, b_elem in zip(a, b):
            if a_elem == "x":
                continue
            elif a_elem == b_elem:
                # print(b)
                continue
            return False
        return True

    @staticmethod
    def filter_by_subject(subjects):
        if not isinstance(subjects, list):
            subjects = [subjects]

        def filter(data):
            for subject in subjects:
                if subject in data["รายวิชา"]:
                    return True

        return filter

    # เช่น เกรด 5 ภาคเรียน
    @staticmethod
    def filter_by_period(period):
        def filter(data):
            if data["ภาคเรียนรวมปัจจุบัน"] <= period:
                return True

        return filter

    def filter(self, filters=[]):
        all_data = []
        for data in self.unordered_data:
            filtered = True
            for filter in filters:
                if not filter(data):
                    filtered = False
                    break
            if filtered:
                all_data.append(data)
        return all_data

    def calculate_gpa(self, data):
        df_column = ["รหัสวิชา","เกรด","หน่วยกิต","ภาคเรียนที่","ปีที่"]
        df_data = []
        df_index = []

        gpa = 0
        total_weight = 0
        for frame in data:
            try:
                gpa += float(frame["เกรด"]) * frame["นก."]
                total_weight += frame["นก."]

                df_data.append([frame["รหัสวิชา"],frame["เกรด"],frame["นก."],frame["ภาคเรียน"],frame["ปี"]])
                df_index.append(frame["รายวิชา"])
            except:
                pass
        df = pd.DataFrame(df_data,columns=df_column,index=df_index)
        #print(float("{:.4f}".format(gpa / total_weight)[:4]),gpa / total_weight)
        try:
            return float("{:.4f}".format(gpa / total_weight)[:4]),df
        except ZeroDivisionError:
            return 0,df

    def get_gpax(self):
        return self.calculate_gpa(self.unordered_data)

    def not_filter(self, filter):
        def niset_filter(data):
            return not filter(data)

        return niset_filter

    def auto_read(self):
        self.reset()
        self.available_period = []
        #print(os.listdir(),os.getcwd())
        os.chdir(self.first_path)
        for file in glob.glob("data/*"):
            file_name = file.split("\\")[-1][:-4]
            year, period = file_name.split("_")
            year, period = int(year), int(period)
            self.available_period.append(f'{year}-{period}')

            self.add_period(file, year, period)

    def auto_determined_possible(self):
        self.possible_gpa = {}
        for field_name in self.all_gpa:
            filter = self.all_gpa[field_name]
            # print(filter)
            if len(self.filter(filter)) != 0:
                self.possible_gpa[field_name] = filter
        return self.possible_gpa

    def get_max_period(self):
        max_period = 0
        for data in self.unordered_data:
            if data["ภาคเรียนรวมปัจจุบัน"] > max_period:
                max_period = data["ภาคเรียนรวมปัจจุบัน"]
        return max_period


by_subject_number = StudentData.filter_by_subject_number
by_period = StudentData.filter_by_period
by_subject = StudentData.filter_by_subject


if __name__ == '__main__':
    student_data = StudentData()
    student_data.auto_read()
    print(student_data.auto_determined_possible())
    # student_data.add_period("data/1_1.xls", 1, 1)
    # student_data.add_period("data/1_2.xls", 1, 2)
    # student_data.add_period("data/2_1.xls", 2, 1)
    # student_data.add_period("data/2_2.xls", 2, 2)

    sel = student_data.filter([student_data.filter_by_subject(science_group)])
    for i in sel:
        print(i)
    print(student_data.calculate_gpa(sel))
