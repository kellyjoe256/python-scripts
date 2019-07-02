#!/usr/bin/env python3
'''\
Python script to rename files or directories in a specified directory/folder
'''

import os
import re


def print_error_message(message):
    '''Prints error message to the terminal/console

    message: Message to be printed
    '''
    CRED = '\33[1m\33[31m'
    CEND = '\033[0m'
    print('\n' + CRED + message + CEND + '\n')


def check_answer(answer, expected_input, allow_empty_answer):
    '''Checks if answer passes a given criteria

    answer: Answer given by user to be checked

    expected_input:
        Input/values against which the user's answer will be checked.
        Can be a list or a tuple or a function/method or a string

    allow_empty_answer:
        Boolean value used to determine if user is allowed to provide
        an answer or not

    returns:
        Boolean of either `True` or `False` if the answer provider by
        user passed the given criteria
    '''
    is_correct = False
    if isinstance(expected_input, (list, tuple,)):
        is_correct = answer.lower() in expected_input
    elif hasattr(expected_input, '__call__'):  # OR callable(expected_input)
        # IF an answer has been given and empty answers are allowed
        # OR IF an answer has been given and we don't allow empty answers
        # OR IF an answer has not been given and we don't allow empty answers
        # THEN call the function/method with the answer as the input
        temp = (answer and allow_empty_answer) \
            or (answer and not allow_empty_answer) \
            or (not answer and not allow_empty_answer)
        if temp:
            is_correct = expected_input(answer)
        else:
            is_correct = True
    else:
        is_correct = (answer.lower() == expected_input)
    return is_correct


def prompt_for_answer(prompt, expected_input=None,
                      error_message=None, allow_empty_answer=False):
    '''Prompts for input from user

    prompt: prompt message

    expected_input:
        Input or values to check provided answer against.
        Default is `None` meaning the no answer has to be provided

    error_message:
        String error message to printed in case user provides an wrong
        answer or value.
        Default is `None` meaning no message is printed

    allow_empty_answer:
        Boolean value used to determine if user is allowed to provide an
        answer or not'.
        Default is `False` answer doesn't have provide an answer

    return: The provided user answer
    '''
    try:
        CBEIGE = '\33[36m'
        CEND = '\033[0m'
        answer = input(CBEIGE + prompt + CEND)
        answer = answer.strip()
        if expected_input:
            is_correct_answer = check_answer(
                answer, expected_input, allow_empty_answer)
            while is_correct_answer is not True:
                if error_message:
                    print_error_message(error_message)
                answer = input(CBEIGE + prompt + CEND)
                is_correct_answer = check_answer(
                    answer, expected_input, allow_empty_answer)
        return answer
    except (KeyboardInterrupt, EOFError):
        print()
        exit()


def get_new_filename(filename, search, replace):
    '''Changes the name of the provided file

    filename: Original name of file to be changed

    search: Character(s) to replaced in the filename

    replace: Character(s) to be used for replacement in filename

    returns: Changed file name
    '''
    regex = None
    if search == ' ':
        regex = r'\s+'
    else:
        regex = r'{0}'.format(re.escape(search))
    filename_parts = re.split(regex, filename)
    return replace.join(filename_parts)


def rename_file(old_filename, new_filename):
    '''Renames a file or directory

    old_filename: File whose name is to be changed

    new_filename: New name of the file

    returns: Boolen `True` or `False` depending on whether file was renamed
    '''
    try:
        os.rename(old_filename, new_filename)  # OR use shutil package
        return True
    except (OSError, PermissionError):
        return False


def rename_files(directory, search, replace,
                 sub_directories=True, rename_directories=False, counter=0):
    '''Traverses a directory and renames files or directories

    directory: Directory or folder in which to rename files

    search: Character(s) to replaced in the filename

    replace: Character(s) to be used for replacement in filename

    sub_directories:
        If `True` even files or directories in sub directories are renamed
        Default is `True`

    rename_directories:
        If `True` even directories will be renamed. Default is `False`

    counter:
        Keeps track of the number of files or directories that have
        been renamed

    returns: How many files or directories have been renamed
    '''
    try:
        os.chdir(directory)
    except (OSError, PermissionError):
        error_message = 'Access to directory "' + directory + '" denied'
        print_error_message(error_message)
        return counter

    directories = []
    for file in os.listdir():
        if os.path.isdir(file):
            if rename_directories and (search in file):
                new_filename = get_new_filename(file, search, replace)
                if rename_file(file, new_filename):
                    counter += 1
                    file = new_filename
            directories.append(os.path.join(os.getcwd(), file))
        elif os.path.isfile(file):
            if search not in file:
                continue
            new_filename = get_new_filename(file, search, replace)
            if rename_file(file, new_filename):
                counter += 1

    if sub_directories and directories:
        for dir_ in directories:
            counter = rename_files(dir_, search, replace, sub_directories,
                                   rename_directories, counter)
    return counter


def main():
    '''Main function where the entire functionality is brought together'''
    directory = prompt_for_answer(
        'Enter directory (if left empty, default is current directory): ',
        os.path.isdir,
        'Please enter a valid directory',
        True)
    directory = directory if directory else '.'

    search_for = prompt_for_answer(
        'Enter character(s) to replace in filenames'
        '(if left empty, default is the space character): ')
    search_for = search_for if search_for else ' '

    replace_with = prompt_for_answer(
        'Enter character(s) to be used for replacement'
        '(if left empty, default is the underscore(_)): ')
    replace_with = replace_with if replace_with else '_'

    sub_directories = prompt_for_answer(
        'Do you want to rename files in sub directories too? yes(y)/no(n): ',
        ('yes', 'y', 'no', 'n',),
        'Please enter either yes(y) or no(n)')
    if sub_directories.lower() in ('yes', 'y',):
        sub_directories = True
    else:
        sub_directories = False

    rename_directories = prompt_for_answer(
        'Do you want to rename directories too? yes(y)/no(n): ',
        ('yes', 'y', 'no', 'n',),
        'Please enter either yes(y) or no(n)')
    if rename_directories.lower() in ('yes', 'y',):
        rename_directories = True
    else:
        rename_directories = False

    kwargs = {
        'directory': directory,
        'search': search_for,
        'replace': replace_with,
        'sub_directories': sub_directories,
        'rename_directories': rename_directories,
    }

    counter = rename_files(**kwargs)

    how_many = ''
    if counter == 1:
        how_many = ' 1 file renamed '
    else:
        how_many = ' ' + str(counter) + ' files renamed '

    print('\n' + how_many.center(100, '*') + '\n')


if __name__ == '__main__':
    main()
