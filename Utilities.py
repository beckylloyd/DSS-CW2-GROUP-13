"""
less than <: &#60;
greater than >: &#62;
open bracket (: &#40;
close bracket ): &#41;
slash /: &#47;
back slash \: &#92;

"""

import re

# regexes from https://owasp.org/www-community/OWASP_Validation_Regex_Repository
EMAIL = r"[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$"
GENERIC = r"^[a-zA-Z0-9 .:!?()-]+$"
PASSWORD = r"^(?:(?=.*\d)(?=.*[A-Z])(?=.*[a-z])|(?=.*\d)(?=.*[^A-Za-z0-9])(?=.*[a-z])|(?=.*[^A-Za-z0-9])(?=.*[A-Z])(?=.*[a-z])|(?=.*\d)(?=.*[A-Z])(?=.*[^A-Za-z0-9]))(?!.*(.)\1{2,})[A-Za-z0-9!~<>,;:_=?*+#.\"&§%°()\|\[\]\-\$\^\@\/]{8,128}$"

match = ['<', '>', '/', '\\']
match_extended = ['<', '>', '/', '\\', ';', ':', '(', ')', '$', '%', '&', '#', '\"', '-']
encoding = [['\'', '&#27;'],
            ['#', '&#35;'],
            ['$', '&#36;'],
            ['%', '&#37;'],
            ['(', '&#40;'],
            [')', '&#41;'],
            ['/', '&#47;'],
            [':', '&#58;'],
            [';', '&#59;'],
            ['=', '&#61;'],
            ['&', '&amp;'],
            ['<', '&lt;'],
            ['>', '&gt;'],
            ['"', '&quot;'] ]

extra_secure = False
use_encoding = False


"""
parse any text
return: bool True if text ok
        string text after parsing 
"""
def parse(text):
    x = re.search(GENERIC, text)
    if x is None:
        # must have been something potentially malicious
        if use_encoding:
            return False, encode(text)
        elif extra_secure:
            return False, strip_text(text, match_extended)
        else:
            return False, strip_text(text, match)
    return True, x.group()

"""
remove any potentially malicious characters from the text
"""
def encode(text):
    new_text = ''
    for c in text:
        added = False
        for pair in encoding:
            if c == pair[0]:
                new_text += pair[1]
                added = True
                break
        if not added:
            new_text += c
    return new_text

"""
remove any potentially malicious characters from the text
"""
def strip_text(text, list):
    new_text =''
    for c in text:
        if c in list:
            new_text += ' '
        else:
            new_text += c

    return new_text

"""
check if email is valid email address
"""
def is_email(email):
    x = re.match(EMAIL, email)
    return not(x is None)

"""
check if password is valid password
"""
def secure_password(password):
    x = re.match(PASSWORD, password)
    return not (x is None)



# if __name__ == '__main__':
#     print("Generic text")
#     print("\t|" + parse("here is some normal text nothing to see here.")[1])
#     print("\t|" + parse("here is some snazzy! text :o it has more stuff in it? :D")[1])
#     print("\t|" + parse("<script>document.alert(\"haha\");</script>;")[1])
#     print("\t|" + parse("' union all select password from users;--")[1])
#
#     print("Extra secure ")
#     extra_secure = True
#     print("\t|" + parse("here is some normal text nothing to see here.")[1])
#     print("\t|" + parse("here is some snazzy! text :o it has more stuff in it? :D")[1])
#     print("\t|" + parse("<script>document.alert(\"haha\");</script>;")[1])
#     print("\t|" + parse("' union all select password from users;--")[1])
#
#     print("Use encoding")
#     use_encoding = True
#     print("\t|" + parse("here is some normal text nothing to see here.")[1])
#     print("\t|" + parse("here is some snazzy! text :o it has more stuff in it? :D")[1])
#     print("\t|" + parse("<script>document.alert(\"haha\");</script>;")[1])
#     print("\t|" + parse("' union all select password from users;--")[1])
#
#     print("\n----- Emails -----")
#     print("katerina.holdsworth@gmail.com = " + str(is_email("katerina.holdsworth@gmail.com")))
#     print("this is not an@ email address.com = " + str(is_email("this is not an@ email address.com")))
#     print("testy@email.w = " + str(is_email("testy@email.w")))
#
#     print("\n----- Passwords -----")
#     print("alllowercase: " , secure_password("alllowercase"))
#     print("short: " , secure_password("short"))
#     print("nONumbERs: " , secure_password("nONumbERs"))
#     print("numbersAnD123: ",  secure_password("numbersAnD123"))
#     print("symBol&*: " , secure_password("symBol&*"))
#     print("eequAl89: " , secure_password("eequAl89"))
#     print("aaaa23E: " , secure_password("aaaa23E"))






