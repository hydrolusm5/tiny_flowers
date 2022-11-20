"""Custom Exceptions"""

class WrongFormatException(Exception):
    """
    WrongFormatException class

    Exception that can be raised when the format type
    given as parameter is not supported.
    """

class WrongMetaFileException(Exception):
    """
    WrongMetaFileException class

    Exception that can be raised when the meta file
    format is not correct.
    """

class NoConfigFileException(Exception):
    """
      NoConfigFileException class

      Exception that can be raised when no Config fil
      is present
      """


class WrongSourceHeaderException(Exception):
    """
    WrongSourceHeaderException class
    Exception that can be raised when the source data
    header has missing column names
    """

class UnknownFileOrginException(Exception):
    """
    WrongSourceHeaderException class
    Exception that can be raised when the source data's
    origin can't be cdefined
    """