from sqlalchemy import and_

import Config
from Config import DEBUG
from Model import *
from Views.Base import RequestHandler
from Views.Utils import get_user


class UpdateHandler(RequestHandler):
    async def post(self):
        session = self.get_session()
        try:
            key = self.get_argument('key')
            if key != Config.SECRET_KEY:
                self.return_status(self.STATUS_PERMISSION_DENIED)
            else:
                sheet_names = ['Sheet1', 'C', 'Python', 'Algorithm', 'Count']

                # Update userdata
                value_order = ['id', 'mail', 'full_name', 'gender_value', 'school',
                    'school_type_value', 'grade', 'address', 'phone',
                    'power', 'rule_test', 'pre_test', 'signup_status']

                values = []
                res = session.query(User, UserData, GenderOption, SchoolTypeOption) \
                    .filter(and_(User.id == UserData.uid,
                                 UserData.gender == GenderOption.id,
                    UserData.school_type == SchoolTypeOption.id)) \
                    .order_by(User.id)
                for row in res:
                    element = row[0].as_dict()
                    del element['password']
                    
                    user_data = row[1].as_dict()
                    del user_data['id']
                    del user_data['uid']                    
                    element.update(user_data)

                    element['gender_value'] = row[2].value
                    element['school_type_value'] = row[3].value

                    value = []
                    for key in value_order:
                        if key == 'rule_test' or key == 'pre_test':
                            value.append('v' if element[key] else '')
                        elif key == 'power':
                            power_list = ['一般', '管理者', '神']
                            if element[key] == -1:
                                value.append('未完成註冊')
                            else:
                                value.append(power_list[element[key]])
                        elif key == 'signup_status':
                            for i in range(3):
                                value.append('v' if element[key] & (1 << i) else '')
                        else:
                            value.append("'" + str(element[key]))
                    values.append(value)

                self.g_sheet.update(values, sheet_names[0] + '!A2:O')

                # For counting
                count_values = [[0, 0], [0, 0], [0, 0], [0, 0]]

                # Update Application
                for class_type in range(1, 4):
                    values = []

                    question_list = []
                    value = ['id', '姓名', '性別', '學校', '年級']
                    res = session.query(ApplicationQuestion) \
                        .filter(and_(ApplicationQuestion.class_type == class_type, ApplicationQuestion.status == 1)) \
                        .order_by(ApplicationQuestion.order)
                    for row in res:
                        question_list.append(row)
                        value.append(row.description)
                    values.append(value)

                    res = session.query(User, UserData) \
                        .filter(and_(User.id == UserData.uid,
                                     User.signup_status.op('&')(1 << (class_type - 1)) > 0)) \
                        .order_by(User.id)
                    for row in res:
                        user_id = row[0].id
                        user = row[1]
                        answer = {}
                        for app_row in session.query(ApplicationAnswer).filter(ApplicationAnswer.uid == row[0].id):
                            answer[app_row.qid] = app_row.description

                        value = []
                        value.append(user_id)
                        value.append(user.full_name)
                        value.append('女' if user.gender == 1 else '男')
                        value.append(user.school)
                        value.append(user.grade)

                        if user_id > Config.MAX_TEST_ID:
                            if class_type > 1:
                                count_values[class_type][0] += 1
                                if user.gender == 1:
                                    count_values[class_type][1] += 1

                        for question in question_list:
                            if question.id in answer:
                                value.append(answer[question.id])
                            else:
                                value.append('')

                            if user_id > Config.MAX_TEST_ID and question.id == Config.C_CLASS_QID and question.id in answer:
                                if answer[question.id].find('竹') >= 0:
                                    count_values[0][0] += 1
                                    if user.gender == 1:
                                        count_values[0][1] += 1
                                if answer[question.id].find('北') >= 0:
                                    count_values[1][0] += 1
                                    if user.gender == 1:
                                        count_values[1][1] += 1

                        values.append(value)
                    self.g_sheet.update(values, sheet_names[class_type] + '!A1:Z')

                self.g_sheet.update(count_values, sheet_names[4] + '!B2:C')

                self.return_status(self.STATUS_SUCCESS)
        except Exception as e:
            if DEBUG:
                print(e)
            self.return_status(self.STATUS_ERROR)
        session.close()
