import json

class StringToIntegerEncoder:
    def __init__(self):
        self.__encode_table = {}
        self.__decode_table = {}
        self.__code = 0

    def encode_from_string(self, string):
        if string not in self.__encode_table:
            self.__encode_table[string] = self.__code
            self.__decode_table[self.__code] = string
            self.__code = self.__code + 1
        return self.__encode_table[string]

    def decode_to_string(self, integer):
        if integer not in self.__decode_table:
            raise ValueError('Integer {} is not encoded before.'.format(integer))
        return self.__decode_table[integer]

    def encode_from_string_list(self, string_list):
        integer_list = [self.encode_from_string(string) for string in string_list]
        integer_list.sort()
        return integer_list

    def decode_to_string_list(self, integer_list):
        try:
            return [self.decode_to_string(integer) for integer in integer_list]
        except:
            raise ValueError('Some integer in integer list are not encoded before.')

    def encode_from_list_of_string_list(self, list_of_string_list):
        return [self.encode_from_string_list(string_list) for string_list in list_of_string_list]

    def decode_to_list_of_string_list(self, list_of_integer_list):
        try:
            return [self.decode_to_string_list(integer_list) for integer_list in list_of_integer_list]
        except:
            raise ValueError('Some part of integer_list are not encoded before.')

class ListToIntegerEncoder:
    def __init__(self):
        self.__encode_table = {}
        self.__decode_table = {}
        self.__code = 0

    def encode_from_list(self, target_list):
        json_string = json.dumps(target_list)
        if json_string not in self.__encode_table:
            self.__encode_table[json_string] = self.__code
            self.__decode_table[self.__code] = json_string
            self.__code = self.__code + 1
        return self.__encode_table[json_string]

    def decode_to_list(self, integer):
        try:
            return json.loads(self.__decode_table[integer])
        except:
            raise ValueError('Integer {} is not encoded before.'.format(integer))


if __name__ == '__main__':
    encoded_source = [
        ['a', 'b', 'c'],
        ['a', 'b', 'ab'],
        ['ab', 'c', 'd'],
    ]
    encoded_answer = [
        [0, 1, 2],
        [0, 1, 3],
        [2, 3, 4], # sorted
    ]
    decoded_source = [
        [0, 1, 2],
        [2, 0, 1],
        [3, 1, 0],
        [4, 4, 4],
    ]
    decoded_answer = [
        ['a', 'b', 'c'],
        ['c', 'a', 'b'],
        ['ab', 'b', 'a'],
        ['d', 'd', 'd'],
    ]
    stie = StringToIntegerEncoder()
    for result, answer in zip(stie.encode_from_list_of_string_list(encoded_source), encoded_answer):
        assert result == answer, 'Bug in `StringToIntegerEncoder.encode_from_list_of_string_list`.'
    for result, answer in zip(stie.decode_to_list_of_string_list(decoded_source), decoded_answer):
        assert result == answer, 'Bug in `StringToIntegerEncoder.decode_to_list_of_string_list`.'

    encoded_source = [
        ['0','1'],
        ['0','1'],
        ['0','2'],
        ['1','2'],
    ]

    encoded_answer = [
        0,
        0,
        1,
        2
    ]

    decoded_source = [
        0,
        1,
        2,
        0
    ]

    decoded_answer = [
        ['0','1'],
        ['0','2'],
        ['1','2'],
        ['0','1'],
    ]

    ltie = ListToIntegerEncoder()
    for source, answer in zip(encoded_source, encoded_answer):
        assert ltie.encode_from_list(source) == answer, 'Bug in `ListToIntegerEncoder.encode_from_list`.'
    for source, answer in zip(decoded_source, decoded_answer):
        assert ltie.decode_to_list(source) == answer, 'Bug in `ListToIntegerEncoder.decode_to_list`.'