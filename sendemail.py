import smtplib
import traceback
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


def sendEmail(source, message, subject, toaddress, fromaddress, filename):

    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = fromaddress
    msg['To'] = toaddress
    # msg.attach(message)

    mainbody = MIMEText(message, 'plain')
    msg.attach(mainbody)

    # Assume we know that the image files are all in PNG format
    # Open the files in binary mode.  Let the MIMEImage class automatically
    # guess the specific image type.
    if (filename != ""):
        fp = open(filename, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)

    # Send the email via our own SMTP server.

    try:
        # open up a line with the server
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.ehlo()
        s.starttls()
        s.ehlo()

        # login, send email, logout
        s.login(config.mailUser, config.mailPassword)
        s.sendmail(config.mailUser, toaddress, msg.as_string())
        # s.close()

        s.quit()

    except:
        if (config.SWDEBUG):
            pass
            print(traceback.format_exc())
            print("sendmail exception raised")
    return 0
