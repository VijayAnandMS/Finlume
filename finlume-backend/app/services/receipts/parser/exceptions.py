class ParseException(Exception): pass
class MissingRequiredFieldException(ParseException): pass
class NumericConsistencyException(ParseException): pass
class InvalidDateFormatException(ParseException): pass
class AmbiguousValueException(ParseException): pass
