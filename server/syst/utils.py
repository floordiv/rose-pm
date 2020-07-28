import string


def validate_name(name):
    whitelist = '._-'
    blacklist = [letter for letter in string.punctuation if letter not in whitelist]

    return not any([letter in name for letter in blacklist])
