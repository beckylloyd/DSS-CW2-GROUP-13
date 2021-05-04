import unittest
import Utilities as util
from datetime import datetime
import time
class MyTestCase(unittest.TestCase):
    def test_email(self):
        self.assertFalse(util.is_email("hello"))
        self.assertTrue(util.is_email("myemail@gmail.com"))
        self.assertFalse(util.is_email("thisisnotan@emailaddress. com"))
        self.assertFalse(util.is_email("testy@email.w"))

    def test_password(self):
        self.assertTrue(util.secure_password("numbersAnD123"))
        self.assertTrue(util.secure_password("symBol&*"))
        self.assertTrue(util.secure_password("eequAl89"))

        self.assertFalse(util.secure_password("alllowercase"))
        self.assertFalse(util.secure_password("short"))
        self.assertFalse(util.secure_password("nONumbERs"))
        self.assertFalse(util.secure_password("aaaa23E"))

    def test_parse(self):
        self.assertEqual(util.parse("here is some normal text nothing to see here."), (True, "here is some normal text nothing to see here."))
        self.assertEqual(util.parse("here is some snazzy! text :o it has more stuff in it? :D"), (True, "here is some snazzy! text :o it has more stuff in it? :D"))
        self.assertEqual(util.parse("<script>document.alert(\"haha\");</script>;"), (False, " script document.alert(\"haha\");  script ;"))
        self.assertEqual(util.parse("' union all select password from users;--"), (False, "' union all select password from users;--"))

    def test_parse_secure(self):
        util.extra_secure = True
        util.use_encoding = False
        self.assertEqual(util.parse("here is some normal text nothing to see here."), (True, "here is some normal text nothing to see here."))
        self.assertEqual(util.parse("here is some snazzy! text :o it has more stuff in it? :D"), (True, "here is some snazzy! text :o it has more stuff in it? :D"))
        self.assertEqual(util.parse("<script>document.alert(\"haha\");</script>;"), (False, " script document.alert  haha     script  "))
        self.assertEqual(util.parse("' union all select password from users;--"), (False, "' union all select password from users   "))

    def test_parse_encode(self):
        util.use_encoding = True
        util.extra_secure = False
        self.assertEqual(util.parse("here is some normal text nothing to see here."), (True, "here is some normal text nothing to see here."))
        self.assertEqual(util.parse("here is some snazzy! text :o it has more stuff in it? :D"), (True, "here is some snazzy! text :o it has more stuff in it? :D"))
        self.assertEqual(util.parse("<script>document.alert(\"haha\");</script>;"), (False, "&lt;script&gt;document.alert&#40;&quot;haha&quot;&#41;&#59;&lt;&#47;script&gt;&#59;"))
        self.assertEqual(util.parse("' union all select password from users;--"), (False, "&#27; union all select password from users&#59;--"))

    def test_encrypt_decrypt(self):
        list = ["simple text", "text3454365", "Symbols£&(*"]
        for text in list:
            cipher_text, encrypt_time = util.encrypt(text)
            plain_text = util.decrypt(cipher_text, encrypt_time)
            self.assertEqual(text, plain_text)

    def test_hash(self):
        list = ["simple text", "text3454365", "Symbols£&(*"]
        for text in list:
            hash_time = datetime.now()
            hash1 = util.hash(text, hash_time)
            hash2 = util.hash(text, hash_time)
            self.assertEqual(hash1, hash2)
            time.sleep(5)
            hash3 = util.hash(text, datetime.now())
            self.assertNotEqual(hash1, hash3)

    def test_hash_equals(self):
        text1 = "here is a very long text for you to hash"
        text2 = "here is a long text that is not the same"
        hash_time = datetime.now()
        hash_1 = util.hash(text1, hash_time)
        hash_2 = util.hash(text2, hash_time)
        self.assertFalse(util.compare_hashes(hash_1, hash_2))
        self.assertTrue(util.compare_hashes(hash_1, hash_1))
        time.sleep(5)
        hash_time = datetime.now()
        hash_3 = util.hash(text1, hash_time)
        self.assertFalse(util.compare_hashes(hash_1, hash_3))

    def test_unencode(self):
        text = [ "here is some snazzy! text :o it has more stuff in it? :D", "<script>document.alert(\"haha\");</script>;", "' union all select password from users;--"]
        for each in text:
            encoded = util.encode(each)
            decoded = util.unencode(encoded)
            self.assertEqual(decoded, each)




if __name__ == '__main__':
    unittest.main()
