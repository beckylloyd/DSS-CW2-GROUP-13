import unittest
import DBConnect as db

class DBTestMethods(unittest.TestCase):
    def test_connection(self):
        self.assertIsNotNone(db.connect())

    def test_select_one(self):
        user = (5, "izzy", "abc123", "izzy@email.com")
        self.assertEqual(db.select_one("SELECT * FROM users WHERE user_id=?;", (5,)), user)
        tag = (1, "Star Wars")
        self.assertEqual(db.select_one("SELECT * FROM tags WHERE tag_id=?;", (1,)), tag)
        post = (3, "Question about duplo","What ages is lego duplo for?", "27/03/2021", "18:25", 3, 3)
        self.assertEqual(db.select_one("SELECT * FROM posts WHERE post_id=?;", (3,)), post)

        self.assertIsNone(db.select_one("DROP TABLE users;", ()))


    def test_select_all(self):
        self.assertIsNotNone(db.select_all("SELECT * FROM users;"))
        self.assertIsNone(db.select_all("DELETE FROM users;"))

    def test_login(self):
        login_ok = (True, "Log in successful :)")
        login_not = (False, "Error logging in :(")

        self.assertEqual(db.login("lottie@email.com", "123password"), login_ok)
        self.assertEqual(db.login("lottie@email.com", "password"), login_not)
        self.assertEqual(db.login("lottie", "password"), login_not)

    def test_search(self):
        self.assertIsNotNone(db.search("lego"))
        self.assertAlmostEqual(db.search("schaufensterpuppen"), [])
        self.assertAlmostEqual(db.search("';ALTER TABLE users RENAME TO malicious;"), [])

    def test_sign_up(self):
        email = "katerina.holdsworth@gmail.com"
        new_email= (True, "An email has been sent to: " + email +" Please check your inbox for more details!")
        old_username = (False, "This username already exists")
        # make sure to remove new3 before running
        #self.assertEqual(db.signUp(email, "new3", "pass"), new_email)
        self.assertEqual(db.signUp(email, "katerina", "pass"), old_username)




if __name__ == '__main__':
    unittest.main()
