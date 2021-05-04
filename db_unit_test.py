import unittest
import DBConnect as db
import random
class DBTestMethods(unittest.TestCase):
    def test_connection(self):
        self.assertIsNotNone(db.connect())

    def test_basic_methods(self):
        # all prints should say not authorised
        # select one
        self.assertIsNotNone(db.select_one("SELECT * FROM users WHERE user_id=?;", (5,)))
        tag = (1, "Star Wars")
        self.assertEqual(db.select_one("SELECT * FROM tags WHERE tag_id=?;", (1,)), tag)
        post = (3, "Question about duplo","What ages is lego duplo for?", "27/03/2021", "18:25", 3, 3)
        self.assertEqual(db.select_one("SELECT * FROM posts WHERE post_id=?;", (3,)), post)

        # select all
        self.assertIsNone(db.select_one("DROP TABLE users;", ()))
        self.assertIsNotNone(db.select_all("SELECT * FROM users;", ()))
        self.assertIsNone(db.select_all("DELETE FROM users;", ()))

        # insert
        self.assertTrue(db.insert("INSERT INTO tags(tag_id, name) VALUES (?, ?)", (20, "newTag")))
        self.assertFalse(db.insert("DELETE FROM tags;", (20, "newTag")))
        self.assertFalse(db.insert("SELECT * FROM users;", ()))
        self.assertFalse(db.insert("UPDATE users SET password=?", ("pass")))

        # update
        self.assertTrue(db.update("UPDATE tags SET name=? WHERE tag_id=?", ("taggy mc tag face", 20)))
        self.assertFalse(db.update("INSERT INTO tags(tag_id, name) VALUES (?, ?)", (20, "newTag")))
        self.assertFalse(db.update("SELECT * from comments;", ()))
        self.assertFalse(db.update("DELETE FROM users;", ()))

        # delete
        self.assertTrue(db.delete("DELETE FROM tags WHERE tag_id=?", (20,)))
        self.assertFalse(db.delete("INSERT INTO tags(tag_id, name) VALUES (?, ?)", (20, "newTag")))
        self.assertFalse(db.delete("SELECT * FROM users;", ()))


    def test_login(self):
        login_ok = (True, "Log in successful :)")
        login_not = (False, "Error logging in :(")

        self.assertEqual(db.login("billy@email.com", "Passwrd23"), login_ok)
        self.assertEqual(db.login("billy@email.com", "password"), login_not)
        self.assertEqual(db.login("billy", "password"), login_not)

    def test_search(self):
        self.assertIsNotNone(db.search("lego"))
        self.assertAlmostEqual(db.search("schaufensterpuppen"), ('schaufensterpuppen', []))
        self.assertEqual(db.search("' union all select password from users;--")[0], "' union all select password from users   ")

    def test_sign_up(self):
        not_email = "Please enter a valid email address!"
        not_password = "Please enter a more secure password!"
        not_username = "Please enter a valid username!"
        username_taken = "That username is already taken!"

        # checking the inputs are valid
        self.assertEqual(db.signUp("not an email", "billy", "Password123")[1], not_email)
        self.assertEqual(db.signUp("billy@email.com", "billy", "pass")[1], not_password)
        self.assertEqual(db.signUp("billy@email.com", "<>;*-billy", "Password123")[1], not_username)
        self.assertEqual(db.signUp("billy@email.com", "billy", "Password123")[1], username_taken)

        #email_sent = "An email has been sent to " + email + " please check your inbox for details!"

        # email sent for new email address
        username = "testy" + str(random.randint(0,100)) + str(random.randint(0,100))
        email = username + "@email.com"
        email_sent = "An email has been sent to " + email + " please check your inbox for details!"
        self.assertEqual(db.signUp(email, username, "Password123")[1], email_sent)
        self.assertEqual(db.users_get_email(username), email)
        # email sent for old email address
        email = "billy@email.com"
        username = "testy" + str(random.randint(0,100)) + str(random.randint(0,100))
        email_sent = "An email has been sent to " + email + " please check your inbox for details!"
        self.assertEqual(db.signUp(email, username, "Password123")[1], email_sent)
        self.assertNotEqual(db.users_get_email(username), email)



if __name__ == '__main__':
    unittest.main()
