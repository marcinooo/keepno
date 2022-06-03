"""
Contains utils for mailing.
"""

import boto3
from typing import List
from flask import Flask
from botocore.exceptions import ClientError


class SES:
    """Class creates object which is extension for keepno app to send email messages."""
    def __init__(self, app: Flask = None):
        self.app = app
        self.client = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initializes SES extension.
        :param app: Flask app
        :return: None
        """
        self.client = boto3.client('ses',
                                   region_name=app.config['AWS_REGION'],
                                   aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                                   aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])

    def send_email(self, subject: str, sender: str, recipients: List[str], text_body: str, html_body: str,
                   charset: str = "UTF-8") -> None:
        """
        Sends email.
        :param subject: mail subject
        :param sender: mail sender
        :param recipients: mail recipients
        :param text_body: mail text body
        :param html_body: mail text html
        :param charset: encoding type
        :return: None
        """
        source = f"Keepno Team <{sender}>"

        try:
            response = self.client.send_email(
                Destination={
                    'ToAddresses': recipients,
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': charset,
                            'Data': html_body,
                        },
                        'Text': {
                            'Charset': charset,
                            'Data': text_body,
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': subject,
                    },
                },
                Source=source,
            )
        except ClientError as error:
            print(error.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
