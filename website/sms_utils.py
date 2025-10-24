from dotenv import load_dotenv
import os
load_dotenv()
from twilio.rest import Client
import phonenumbers


account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_sid = os.getenv("TWILIO_VERIFY_SID")

client = Client(account_sid, auth_token)

def format_phone_e164(number, region="US"):
    parsed = phonenumbers.parse(number, region)
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

def send_verification_code(phone_number: str):
    formatted_number = format_phone_e164(phone_number)
    verification = client.verify.v2.services(verify_sid).verifications.create(
        to=formatted_number,
        channel="sms"
    )
    print(f"Sent verification: SID={verification.sid}, Status={verification.status}")
    return verification.status

def check_verification_code(phone_number: str, code: str):
    formatted_number = format_phone_e164(phone_number)
    verification_check = client.verify.v2.services(verify_sid).verification_checks.create(
        to=formatted_number,
        code=code
    )
    print(f"Verification check: SID={verification_check.sid}, Status={verification_check.status}")
    return verification_check.status




