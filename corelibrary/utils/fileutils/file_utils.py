"""
Created on 29.07.2016

Some static helper methods to read and write files.
"""
import os
import shutil
from filename import FileName


def write_file_text(full_file_name, text, create_dir=True):
    """
    Writes the given text string in the file. If flag 'create_dir' is True,
    then the directory is created, if it not exists.
    """
    if create_dir:
        dir_name = os.path.dirname(full_file_name)
        create_directory(dir_name)
    with open(full_file_name, "w") as the_file:
        the_file.write(text)


def write_lines_to_file(full_file_name, text_lines, new_line_sign="\n\r"):
    """
    Writes the given list of lines to the file 'full_file_name'.
    """
    write_file_text(full_file_name, new_line_sign.join(text_lines))


def read_file_lines(full_file_name):
    """
    Reads the text from the file and returns a list of the lines.
    """
    with open(full_file_name, "r") as the_file:
        return the_file.readlines()


def read_file_text(full_file_name):
    """
    Reads the text from the file and returns it as a string.
    """
    with open(full_file_name, "r") as the_file:
        return the_file.read()


def replace_file_extension(full_file_name, new_extension):
    """
    Renames the file extension of the given file.
    """
    return rename_file(full_file_name, extension=new_extension)


def replace_file_name(full_file_name, new_file_name):
    """
    Renames the name of the file. Extension and directory states the same.
    """
    return rename_file(full_file_name, name=new_file_name)


def rename_file(full_file_name, name=None, extension=None, dir_name=None):
    """
    Renames the file 'full_file_name', by the name, extension and dir_name.
    """
    file_name_obj = FileName.create_from_full_name(full_file_name)
    if not name is None:
        file_name_obj.name_without_extension = name
    if not extension is None:
        file_name_obj.extension = extension
    if not dir_name is None:
        file_name_obj.dir_name = dir_name
    return file_name_obj.get_full_file_name()


def list_file_names(directory, extension_filter=None, file_name_filter=None, recursive=True):
    '''
    list the file names of the given directory, where the files are filtered with the extension filter and file_name_filter.
    :param directory:
    :param extension_filter: A function which takes the extension string and returns a boolean.
    :param file_name_filter: A function which takes the file name string and returns a boolean.
    :param recursive: If True all subdirectories are included
    :return:
    '''
    ext_filter = extension_filter if extension_filter is not None else lambda x : True
    name_filter = file_name_filter if file_name_filter is not None else lambda x : True
    ret = []
    for f in os.listdir(directory):
        full_name = os.path.join(directory,f)
        if f.startswith("."):
            continue
        if not os.path.isfile(full_name):
            if recursive:
                ret = ret + list_file_names(full_name, extension_filter, file_name_filter, recursive)
            continue
        fn = FileName.create_from_full_name(full_name)
        if ext_filter(fn.extension) and name_filter(fn.name_without_extension):
            ret.append(full_name)
    return ret


def copy_file(source_full_file_name, destination_full_file_name=None):
    def get_destination_full_file_name(destination_full_file_name):
        destination = destination_full_file_name
        if destination is None:
            fn = FileName(source_full_file_name)
            fn.name_without_extension = fn.name_without_extension + "_copy"
            fn2 = FileName(fn.full_file_name)
            k = 0
            while os.path.exists(fn2.full_file_name):
                fn2.name_without_extension = fn.name_without_extension + str(k)
                k = k + 1
        return fn2

    dest_fn = get_destination_full_file_name(destination_full_file_name)
    if not os.path.exists(dest_fn.dir_name):
        os.mkdir(dest_fn.dir_name)
    shutil.copy2(source_full_file_name, dest_fn.full_file_name)


def create_directory(dir_name):
    subs = dir_name.split(os.path.sep)
    sub_path = os.path.sep
    for i in xrange(len(subs)):
        sub_path = os.path.join(sub_path, subs[i])
        if not os.path.exists(sub_path):
            os.mkdir(sub_path)
