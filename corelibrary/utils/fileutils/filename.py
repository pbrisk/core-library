import os


class FileName(object):
    """
    A file name consist of a name, a directory name and an extension.
    """

    def __init__(self, dir_name, file_name, extension, extension_separator="."):
        self.dir_name = dir_name
        self.name_without_extension = file_name
        self.extension = extension
        self.extension_separator = extension_separator

    @staticmethod
    def create_from_full_name(full_file_name):
        """
        Creates a FileName object from a full_file_name.
        """
        path_and_file = os.path.split(full_file_name)
        directory = FileName._get_abs_path(path_and_file[0])
        name_and_ext = os.path.splitext(path_and_file[1])
        extsep = name_and_ext[1][0]
        ext = name_and_ext[1][1:len(name_and_ext[1])]
        return FileName(directory, name_and_ext[0], ext, extension_separator=extsep)

    @staticmethod
    def _get_abs_path(path):
        if os.path.isabs(path):
            return path
        return os.path.abspath(path)

    def get_full_file_name(self):
        return os.path.join(self.dir_name, \
                            self.name_without_extension + self.extension_separator + self.extension)

    def get_name_with_extension(self):
        return self.name_without_extension + self.extension_separator + self.extension

    def get_fullname_without_extension(self):
        return os.path.join(self.dir_name, self.name_without_extension)

    full_file_name = property(get_full_file_name)
    name_with_extension = property(get_name_with_extension)
    fullname_without_extension = property(get_fullname_without_extension)

    def __str__(self):
        return self.name_with_extension

    def replace_dir(self, new_dir_name):
        """
        Replaces the directory. The name and extension remains the same.
        """
        return FileName(new_dir_name, self.name_without_extension, self.extension)
