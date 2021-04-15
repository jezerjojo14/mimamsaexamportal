import json
import csv
import smtplib, ssl

# port = 465  # For SSL
# password = input("Type your password and press enter: ")
#
# # Create a secure SSL context
# context = ssl.create_default_context()

# Opening JSON file
f = open('password-list.json',)

# returns JSON object as
# a dictionary
passwords = json.load(f)

with open('input2.csv','r') as csvinput:
    with open('output2.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)

        all = []
        row = next(reader)
        row.append('Password 1')
        row.append('Password 2')
        row.append('Password 3')
        row.append('Password 4')
        all.append(row)

        for row in reader:
            print(row)
            if row[8]!="":
                row.append(passwords[(row[8]).lower()])
            else:
                row.append("")
            if row[13]!="":
                row.append(passwords[(row[13]).lower()])
            else:
                row.append("")
            if row[18]!="":
                row.append(passwords[(row[18]).lower()])
            else:
                row.append("")
            if row[23]!="":
                row.append(passwords[(row[23]).lower()])
            else:
                row.append("")
            all.append(row)

        writer.writerows(all)

# with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#     for email in passwords:
#         sender_email = "mimamsatest@gmail.com"
#         receiver_email = email
#         message = """\
#         Subject: Mimamsa Test Password
#
#         Your password is """+passwords[email]
#         server.login("mimamsatest@gmail.com", password)
#         server.sendmail(sender_email, receiver_email, message)
