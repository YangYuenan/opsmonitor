# -*- coding: utf-8 -*-

__author__ = 'tsnav-yangyn'

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import make_header
from email.header import Header


def mail(smtpServer, loginUser, loginPassword, mailFrom, mailTo, mailReceivers,
         mailSubject, mailText, smtpPort=25,fileList=[]):
    assert isinstance(mailReceivers, list)
    assert isinstance(fileList, list)
    sender = mailFrom
    receivers = mailReceivers  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header(mailFrom)
    message['To'] = Header(mailTo)
    subject = mailSubject
    message['Subject'] = Header(subject, 'utf-8')

    # 邮件正文内容
    text = mailText
    message.attach(MIMEText(text, 'plain', 'utf-8'))

    # 构造附件，传送当前目录下的 test.txt 文件
    for filePath in fileList:
        filePath = filePath.decode('utf8')
        fileName = os.path.basename(filePath)
        if os.path.isfile(filePath):
            att = MIMEText(open(filePath, 'rb').read(), 'base64', 'UTF-8')
            att["Content-Type"] = 'application/octet-stream;name="%s"' % make_header([(fileName, 'UTF-8')]).encode(
                'UTF-8')
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            # att["Content-Disposition"] = 'attachment;filename=%s'%fileName
            att["Content-Disposition"] = 'attachment;filename= "%s"' % make_header([(fileName, 'UTF-8')]).encode(
                'UTF-8')
            message.attach(att)
    try:
        server = smtplib.SMTP()
        server.connect(host=smtpServer, port=smtpPort)
        if not smtpPort == 25:
            server.starttls(smtpServer)
        server.login(loginUser, loginPassword)
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
        # smtpObj = smtplib.SMTP('localhost')
        # smtpObj.sendmail(sender, receivers, message.as_string())
        # smtpObj.quit()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(str(e))
        print("Error: 无法发送邮件")
