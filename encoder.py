"""Module of encoder.

StringToIntegerEncoder encode string into integer.
ListToIntegerEncoder encode list into integer.
See test section for code example.
"""

import json

class StringToIntegerEncoder:
    """Encode string into integer. """

    def __init__(self):
        """Use dict object to hash string.

        `__encode_table` will hash string into integer.
        `__decode_table` will hash integer into string.
        `__code` stands for current hash integer range.
        """
        self.__encode_table = {}
        self.__decode_table = {}
        self.__code = 0

    def encode_from_string(self, string):
        """Encode string into integer.

        If `string` is not seen before, use `__code` to represent `string`.

        Args:
            string (str):
                Target string to encode.

        Returns:
            int:
                Encoded integer.
        """

        if string not in self.__encode_table:
            self.__encode_table[string] = self.__code
            self.__decode_table[self.__code] = string
            self.__code = self.__code + 1
        return self.__encode_table[string]

    def decode_to_string(self, integer):
        """Decode integer into string.

        Args:
            integer (int):
                Target integer to decode.

        Returns:
            str:
                Decoded string.

        Raises:
            ValueError:
                If integer is not seen before.
        """

        if integer not in self.__decode_table:
            raise ValueError('Integer {} is not encoded before.'.format(integer))
        return self.__decode_table[integer]

    def encode_from_string_list(self, string_list):
        """Encode list of strings into list of integers.

        Sort encoded result by ascending order.

        Args:
            string_list (list of str):
                Target list of string to encode.

        Returns:
            list of int:
                Encoded list of integers.
        """

        integer_list = [self.encode_from_string(string) for string in string_list]
        integer_list.sort()
        return integer_list

    def decode_to_string_list(self, integer_list):
        """Decode list of integers into list of string.

        Args:
            integer_list (list of int):
                Target list of integers to decode.

        Returns:
            list of str:
                Decoded list of strings.

        Raises:
            ValueError:
                If decode process raise error.
        """

        try:
            return [self.decode_to_string(integer) for integer in integer_list]
        except:
            raise ValueError('Some integer in integer list are not encoded before.')

    def encode_from_list_of_string_list(self, list_of_string_list):
        """Encode list of list of strings into list of list of integers.

        Args:
            list_of_string_list (list of list of str):
                Target list of list of string to encode.

        Returns:
            list of list of int:
                Encoded list of list of integers.
        """

        return [self.encode_from_string_list(string_list) for string_list in list_of_string_list]

    def decode_to_list_of_string_list(self, list_of_integer_list):
        """Decode list of list of integers into list of list of string.

        Args:
            list_of_integer_list (list of list of int):
                Target list of list of integers to decode.

        Returns:
            list of list of str:
                Decoded list of list of strings.

        Raises:
            ValueError:
                If decode process raise error.
        """

        try:
            return [self
                    .decode_to_string_list(integer_list)
                    for integer_list in list_of_integer_list]
        except:
            raise ValueError('Some part of integer_list are not encoded before.')

class ListToIntegerEncoder:
    """Encode list into integer."""

    def __init__(self):
        """Use dict object to hash list.

        `__encode_table` will hash list into integer.
        `__decode_table` will hash integer into list.
        `__code` stands for current hash integer range.
        """
        self.__encode_table = {}
        self.__decode_table = {}
        self.__code = 0

    def encode_from_list(self, target_list):
        """Encode list into integer.

        Using `json.dumps` to convert list into string, then hash string into integer.
        If `target_list` is not seen before, use `__code` to represent `target_list`.

        Args:
            target_list (list):
                Target list to encode.

        Returns:
            int:
                Encoded integer.
        """

        json_string = json.dumps(target_list)
        if json_string not in self.__encode_table:
            self.__encode_table[json_string] = self.__code
            self.__decode_table[self.__code] = json_string
            self.__code = self.__code + 1
        return self.__encode_table[json_string]

    def decode_to_list(self, integer):
        """Decode integer into list.

        Args:
            integer (int):
                Target integer to decode.

        Returns:
            list:
                Decoded list.

        Raises:
            ValueError:
                If integer is not seen before.
        """

        try:
            return json.loads(self.__decode_table[integer])
        except:
            raise ValueError('Integer {} is not encoded before.'.format(integer))

# Test section.
if __name__ == '__main__':
    ENCODED_SOURCE = [
        ['a', 'b', 'c'],
        ['a', 'b', 'ab'],
        ['ab', 'c', 'd'],
    ]
    ENCODED_ANSWER = [
        [0, 1, 2],
        [0, 1, 3],
        [2, 3, 4], # sorted
    ]
    DECODED_SOURCE = [
        [0, 1, 2],
        [2, 0, 1],
        [3, 1, 0],
        [4, 4, 4],
    ]
    DECODED_ANSWER = [
        ['a', 'b', 'c'],
        ['c', 'a', 'b'],
        ['ab', 'b', 'a'],
        ['d', 'd', 'd'],
    ]
    STIE = StringToIntegerEncoder()
    for result, answer in zip(STIE.encode_from_list_of_string_list(ENCODED_SOURCE), ENCODED_ANSWER):
        assert result == answer, 'Bug in `StringToIntegerEncoder.encode_from_list_of_string_list`.'
    for result, answer in zip(STIE.decode_to_list_of_string_list(DECODED_SOURCE), DECODED_ANSWER):
        assert result == answer, 'Bug in `StringToIntegerEncoder.decode_to_list_of_string_list`.'

    ENCODED_SOURCE = [
        ['0', '1'],
        ['0', '1'],
        ['0', '2'],
        ['1', '2'],
    ]

    ENCODED_ANSWER = [
        0,
        0,
        1,
        2
    ]

    DECODED_SOURCE = [
        0,
        1,
        2,
        0
    ]

    DECODED_ANSWER = [
        ['0', '1'],
        ['0', '2'],
        ['1', '2'],
        ['0', '1'],
    ]

    LTIE = ListToIntegerEncoder()
    for source, answer in zip(ENCODED_SOURCE, ENCODED_ANSWER):
        assert LTIE.encode_from_list(source) == answer, \
            'Bug in `ListToIntegerEncoder.encode_from_list`.'
    for source, answer in zip(DECODED_SOURCE, DECODED_ANSWER):
        assert LTIE.decode_to_list(source) == answer, \
            'Bug in `ListToIntegerEncoder.decode_to_list`.'
