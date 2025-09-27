```python
class EmailNotification:
    def __init__(self, recipients, subject, body):
        self.recipients = recipients
        self.subject = subject
        self.body = body

    def sendEmail(self):
        #  Implementation to send email using a library like smtplib or a third-party service.  This is a placeholder.
        try:
            # Simulate sending email. Replace with actual email sending logic.
            print(f"Sending email to {self.recipients}: Subject: {self.subject}, Body: {self.body}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False