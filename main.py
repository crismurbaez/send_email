# -*- coding: utf-8 -*-
from flask import Flask
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
import json


load_dotenv()
app = Flask(__name__)


def send_email(company, destinatario, asunto):
    # envío de emails
    remitente = os.getenv("USER")
    # destinatario = os.getenv("DEST")

    password = os.getenv("PASS")

    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    with open("carta.html", "r") as carta:
        html = carta.read()
    html = html.replace("company", company)

    msg.attach(MIMEText(html, "html"))

    with open("Cristina_Murguia_CV.pdf", "rb") as cv:
        adjunto = cv.read()
    adjunto_MIME = MIMEBase("application", "octet-stream")
    adjunto_MIME.set_payload((adjunto))
    encoders.encode_base64(adjunto_MIME)
    adjunto_MIME.add_header(
        "Content-Disposition", "attachment; filename=Cristina_Murguia_CV.pdf"
    )

    msg.attach(adjunto_MIME)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(remitente, password)

    server.sendmail(remitente, destinatario, msg.as_string())

    server.quit()


def get_company():
    # pedido a base de datos información de la empresa
    URL_REQUEST_EMP = os.getenv("URL_REQUEST")
    URL_REQUEST_ERROR_ = os.getenv("URL_REQUEST_ERROR")
    # colocar en code=1  <----------
    # límite = 256  <-------
    code = 257
    límite = 264
    Error = []
    while code < límite:
        url_empresa = URL_REQUEST_EMP + str(code)
        print(url_empresa)
        response = requests.get(url_empresa)
        if response.status_code == 200:
            # conversión de bytes a diccionario
            response_dict = json.loads(response.content)
            name = response_dict["name"]
            email = response_dict["email"]
            print(name, email)
            asunto = "Ofrezco mis servicios "
            send_email(name, email, asunto)
        else:
            print("Error: " + str(response.content))
            Error.append(str(response.content) + " " + name + " " + email)
        code += 1
    print("envío de emails terminado")
    print(Error)

    # guardo errores en base de datos
    payload = {"Errores": Error}
    response = requests.post(URL_REQUEST_ERROR_, json=payload)
    print(response.url)

    if response.status_code == 200:
        print(response.content)


get_company()
