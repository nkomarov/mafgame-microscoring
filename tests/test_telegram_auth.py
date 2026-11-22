import hashlib
import hmac
import json
import time
import unittest
from urllib.parse import urlencode
from api.telegram_auth import verify_init_data

TOKEN = "123456:TEST"

def signed(data):
    check = "\n".join(f"{k}={v}" for k,v in sorted(data.items()))
    secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    digest = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode({**data, "hash":digest})

class TelegramAuthTests(unittest.TestCase):
    def test_valid(self):
        data={"auth_date":str(int(time.time())),"user":json.dumps({"id":1234})}
        self.assertEqual(verify_init_data(signed(data),TOKEN)["id"],1234)
    def test_tampered(self):
        data={"auth_date":str(int(time.time())),"user":json.dumps({"id":1234})}
        self.assertIsNone(verify_init_data(signed(data).replace("1234","1235"),TOKEN))
    def test_expired(self):
        data={"auth_date":str(int(time.time())-7200),"user":json.dumps({"id":1234})}
        self.assertIsNone(verify_init_data(signed(data),TOKEN))
    def test_duplicates(self):
        data={"auth_date":str(int(time.time())),"user":json.dumps({"id":1234})}
        self.assertIsNone(verify_init_data(signed(data)+"&auth_date=1",TOKEN))

if __name__=="__main__":
    unittest.main()
