# import datetime
# import smtplib
# import ssl
# from email.mime.text import MIMEText

# # 以下にGmailの設定を書き込む★ --- (*1)
# gmail_account = "dada.00131@gmail.com"
# gmail_password = "pCzd8HFEX3Q9qLUwqHG29ZwRK"
# # メールの送信先★ --- (*2)
# mail_to = "dada.00131@gmail.com"

# # メールデータ(MIME)の作成 --- (*3)
# subject = "メール送信テスト"
# body = "メール送信テスト\n"
# body += "メール送信テスdddddddト\n"
# msg = MIMEText(body, "html")
# msg["Subject"] = subject
# msg["To"] = mail_to
# msg["From"] = gmail_account

# # Gmailに接続 --- (*4)
# server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
# server.login(gmail_account, gmail_password)
# server.send_message(msg)  # メールの送信
# print("ok.")

import codecs
import datetime
import smtplib

# import ssl
import sys
from email.mime.text import MIMEText


def main():
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    gmail_account = "dada.00131@gmail.com"
    gmail_password = "pCzd8HFEX3Q9qLUwqHG29ZwRK"
    mail_to = "dada.00131@gmail.com"
    name = "ore"

    today_date = datetime.date.today()
    delivery_date = today_date + datetime.timedelta(days=7)
    # print(today_date, delivery_date)

    subject = "{0}様、発注書の送付について".format(name)
    body = "{0}の発注書をお送りいたします。".format(delivery_date)

    msg = MIMEText(body, "html")

    msg["Subject"] = subject
    msg["To"] = mail_to
    msg["From"] = gmail_account
    # print(msg)

    server = smtplib.SMTP_SSL(
        # "smtp.gmail.com", 465, context=ssl.create_default_context()
        "smtp.gmail.com",
        465,
    )
    server.login(gmail_account, gmail_password)
    server.send_message(msg)
    print("送信完了")


main()
