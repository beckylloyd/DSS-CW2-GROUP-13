"""
less than <: &#60;
greater than >: &#62;
open bracket (: &#40;
close bracket ): &#41;
slash /: &#47;
back slash \: &#92;

"""
import csv
import re
from datetime import datetime
import time


# regexes from https://owasp.org/www-community/OWASP_Validation_Regex_Repository
EMAIL = r"[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$"
GENERIC = r"^[a-zA-Z0-9 .:!?()-]+$"
PASSWORD = r"^(?:(?=.*\d)(?=.*[A-Z])(?=.*[a-z])|(?=.*\d)(?=.*[^A-Za-z0-9])(?=.*[a-z])|(?=.*[^A-Za-z0-9])(?=.*[A-Z])(?=.*[a-z])|(?=.*\d)(?=.*[A-Z])(?=.*[^A-Za-z0-9]))(?!.*(.)\1{2,})[A-Za-z0-9!~<>,;:_=?*+#.\"&§%°()\|\[\]\-\$\^\@\/]{8,128}$"

match = ['<', '>', '/', '\\']
match_extended = [';', '#','<', '>', '/', '\\', ':', '(', ')', '$', '%', '&',  '\"', '-']
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

def unencode(text):
    temp = text.split()
    for pair in encoding:
        text = text.replace(pair[1], pair[0])
    return text

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

"""
encrypt text 
text: text to encrypt

return: the encrypted text
        the time used when encrypting 
"""
def encrypt(text):
    encrypt_time = datetime.now()
    time_hash = round(encrypt_time.time().microsecond * 1000)
    cipher_text = ''
    for character in text:
        character_ascii = (ord(character))
        hashed = time_hash * character_ascii
        cipher_text += str(hashed) + '.'
    return cipher_text, encrypt_time

"""
decrypt text
cipher_text: the encryped text
encrypt_time: time the text was encrypted

return: the plain text 
"""
def decrypt(cipher_text, encrypt_time):
    time_hash = round(encrypt_time.time().microsecond * 1000)
    plain_text = ''
    hashes = cipher_text.split('.')
    for hash in hashes:
        hash_int = 0
        try:
            hash_int = int(hash)
        except:
            break
        character_ascii = int(hash_int/time_hash)
        plain_text += chr(character_ascii)
    return plain_text

"""
one way hashing function
text: text to be hashed
time: time to use when hashing

return: hashed text 
"""
def hash(text, hash_time):
    time_hash = round(hash_time.timestamp() * 1000)
    cipher_text = ''
    for character in text:
        character_ascii = (ord(character))
        hashed = time_hash * character_ascii
        cipher_text += str(hashed)
    return cipher_text

# Function to read a csv file, add each row into a list and return the list
def readFile(aFile):
    file = open(aFile, "r")
    aList = []
    for each in file.readlines():
        aList.append(each.replace("\n", ''))
    file.close()
    return aList


# Function to write to a list and save back to csv file
def writeFile(aList, aFile):
    file = open(aFile, "w")
    for each in aList:
        file.write(each + "\n")
    file.close()

#if __name__ == '__main__':

#     text = input("enter some text to encrypt and decrypt: ")
#     cipher, encrypt_time = encrypt(text)
#     print(cipher)
#     plain = decrypt(cipher, encrypt_time)
#     print(plain)
#     print(plain == text)
#
#     text = input("enter some text to hash: ")
#     hash_time = datetime.now()
#     hash1 = hash(text, hash_time)
#     time.sleep(60)
#     hash2 = hash(text, hash_time)
#     print(hash1 == hash2)
#     text = "<script>document.alert(\"haha\");</script>;"
#     encoded = encode(text)
#     print("encoded: " , encoded)
#     decoded = unencode(encoded)
#     print("decoded: ",decoded )
#     print(text == decoded)






