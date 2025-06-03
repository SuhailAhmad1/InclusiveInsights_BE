import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.utils import formataddr
from config import SENDER_EMAIL, EMAIL_PASSWORD


env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"])
)


def sendSubmitEmail(data):
    template = env.get_template("new_submission_email.html")
    html_content = template.render(
        title=data["title"],
        author=data["author"],
        category=data["category"],
        submission_link=data["submission_link"]
    )

    msg = MIMEMultipart()
    msg['From'] = formataddr(("Inclusive Insights", SENDER_EMAIL))
    msg['To'] = SENDER_EMAIL
    msg['Subject'] = f'New Submission Recieved : "{data["title"]}"'

    # Attach the HTML content to the email message
    msg.attach(MIMEText(html_content, "html"))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.close()

        return True
    except Exception as e:
        print(e)
        return False


def sendPublishedMail(data):
    template = env.get_template("publication_confirmation_email.html")
    html_content = template.render(
        title=data["title"],
        author=data["author"],
        publication_link=data["publication_link"]
    )

    msg = MIMEMultipart()
    msg['From'] = formataddr(("Inclusive Insights", SENDER_EMAIL))
    msg['To'] = data["user_email"]
    msg['Subject'] = f"Congratulations! Your Submission Has Been Published on Inclusive Insights"

    # Attach the HTML content to the email message
    msg.attach(MIMEText(html_content, "html"))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.close()

        return True
    except Exception as e:
        print(e)
        return False


def sendRejectionMail(data):
    template = env.get_template("rejection_email.html")
    html_content = template.render(
        title=data["title"],
        author=data["author"]    
    )

    msg = MIMEMultipart()
    msg['From'] = formataddr(("Inclusive Insights", SENDER_EMAIL))
    msg['To'] = data["user_email"]
    msg['Subject'] = f'Update on Your Submission: "{data["title"]}"'

    # Attach the HTML content to the email message
    msg.attach(MIMEText(html_content, "html"))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.close()

        return True
    except Exception as e:
        print(e)
        return False
