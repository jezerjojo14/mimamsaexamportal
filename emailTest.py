import smtplib, ssl

passwords={
    "vatsal.garg@students.iiserpune.ac.in" : "V9RBFY5T",
    "neev.shah@students.iiserpune.ac.in" : "Y4JZIH48",
    "garvit.agarwal@students.iiserpune.ac.in" : "WZPXGJAW",
    "amogh.rakesh@students.iiserpune.ac.in" : "VN2381XK",
    "shah.varun@students.iiserpune.ac.in" : "70GEN3MK",
    "shah.neel@students.iiserpune.ac.in" : "CKORH0OE",
    "divyansh.gupta@students.iiserpune.ac.in" : "DUR80QGT",
    "aniketh.sivakumar@students.iiserpune.ac.in" : "EZDDMJEH",
    "pallav.khandekar@students.iiserpune.ac.in" : "7BFB5LYV",
    "amogh.ranade@students.iiserpune.ac.in" : "7GM9JI7P",
    "aditya.pujari@students.iiserpune.ac.in" : "3M56MAW6",
}

port = 465  # For SSL
password = input("Type your password and press enter: ")

# Create a secure SSL context
context = ssl.create_default_context()


with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    for email in passwords:
        sender_email = "mimamsatest@gmail.com"
        receiver_email = email
        message = """\
        Subject: Mimamsa Test Password

        Your password is """+passwords[email]
        server.login("mimamsatest@gmail.com", password)
        server.sendmail(sender_email, receiver_email, message)
