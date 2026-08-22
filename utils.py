from kavenegar import KavenegarAPI
from random import randint

def generate_otp():
    return randint(1000, 9999)

def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI('74466A6C5852626F756D31377A373543426A4F31326D6E574C327179664C75522B6C5347754A47324A45303D')
        params = { 'sender' : '2000660110', 'receptor': phone_number, 'message' : f'Hiii ;) Your verify code is: {code}' }
        response = api.sms_send(params)
        print(response)
    except Exception as e:
        print(e)
