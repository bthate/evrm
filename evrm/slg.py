# This file is placed in the Public Domain

txt = "http://genocide.rtfd.io otp.informationdesk@icc-cpi.int OTP-CR-117/19"

def register(k):
    k.addcmd(slg)

def slg(event):
    event.reply(txt)
