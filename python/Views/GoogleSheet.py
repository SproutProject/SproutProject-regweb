import Config

from Views.Base import RequestHandler
from Views.Utils import get_user


class UpdateHandler(RequestHandler):
    async def post(self):
        db = await self.get_db()
        try:
            key = self.get_argument('key')
            if key != Config.SECRET_KEY:
                self.write({'status': 'PERMISSION DENIED'})
            else:
                sheet_names = ['Sheet1', 'C', 'Python', 'Algorithm', 'Count']

                # Update userdata
                value_order = ['id', 'mail', 'full_name', 'gender_value', 'school',
                    'school_type_value', 'grade', 'address', 'phone',
                    'power', 'rule_test', 'pre_test', 'signup_status']

                values = []
                async for row in db.execute(
                    'SELECT u."id", u."mail", u."power", u."rule_test", u."pre_test", u."signup_status",'
                    ' g."value" as "gender_value", s."value" as "school_type_value",'
                    ' d."full_name", d."gender", d."school", d."school_type", d."grade", d."phone", d."address"'
                    ' FROM "user" u'
                    ' JOIN "user_data" d ON u."id"=d."uid"'
                    ' JOIN "gender_option" g ON d."gender"=g."id"'
                    ' JOIN "school_type_option" s ON d."school_type"=s."id"'
                    ' ORDER BY u."id"'
                ):
                    value = []
                    for key in value_order:
                        if key == 'rule_test' or key == 'pre_test':
                            value.append('v' if row[key] else '')
                        elif key == 'power':
                            power_list = ['一般', '管理者', '神']
                            if row[key] == -1:
                                value.append('未完成註冊')
                            else:
                                value.append(power_list[row[key]])
                        elif key == 'signup_status':
                            for i in range(3):
                                value.append('v' if row[key] & (1 << i) else '')
                        else:
                            value.append("'" + str(row[key]))
                    values.append(value)

                self.g_sheet.update(values, sheet_names[0] + '!A2:O')

                # For counting
                count_values = [[0, 0], [0, 0], [0, 0], [0, 0]]

                # Update Application
                for class_type in range(1, 4):
                    values = []

                    question_list = []
                    value = ['id', '姓名', '性別', '學校', '年級']
                    async for row in db.execute(
                        'SELECT * FROM "application_question" WHERE "class_type"=%s AND "status"=1 ORDER BY "order"',
                        (class_type)
                    ):
                        question_list.append(row)
                        value.append(row.description)
                    values.append(value)

                    async for user in db.execute(
                        'SELECT u."id", d."full_name", d."school", d."grade", d."gender" FROM "user" u'
                        ' JOIN "user_data" d'
                        ' ON u."id"=d."uid"'
                        ' WHERE (u."signup_status" & %s) > 0'
                        ' ORDER BY u."id"',
                        (1 << (class_type - 1), )
                    ):
                        answer = {}
                        async for row in db.execute(
                            'SELECT * FROM "application_answer" WHERE "uid"=%s',
                            (user.id, )
                        ):
                            answer[row.qid] = row.description

                        value = []
                        value.append(user.id)
                        value.append(user.full_name)
                        value.append('女' if user.gender == 1 else '男')
                        value.append(user.school)
                        value.append(user.grade)

                        if user.id > 28:
                            if class_type > 1:
                                count_values[class_type][0] += 1
                                if user.gender == 1:
                                    count_values[class_type][1] += 1

                        for question in question_list:
                            if question.id in answer:
                                value.append(answer[question.id])
                            else:
                                value.append('')

                            if user.id > 28 and question.id == 42 and question.id in answer:
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

                self.write({'status': 'SUCCESS'})
        except Exception as e:
            if DEBUG:
                print(e)
            self.write({'status': 'ERROR'})
        await db.close()
