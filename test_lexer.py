import unittest
from lexer import Lexer

class TestLexer(unittest.TestCase):

    def setUp(self):
        # Dummy source code directly string ke roop mein dete hain
        self.code = ["x = 10 + 2\n"]
        
        # Mock Lexer class to override file reading
        class TestableLexer(Lexer):
            def load_source_code(self_inner):
                return self.code  # Use our test string instead of reading a file

        self.lexer = TestableLexer("mock_file.py")  # Filename koi bhi ho sakta hai

    def test_basic_expression(self):
        expected_tokens = [
            ('IDENTIFIER', 'x'),
            ('OPERATOR', '='),
            ('NUMBER', '10'),
            ('OPERATOR', '+'),
            ('NUMBER', '2')
        ]
        tokens = self.lexer.tokenize()
        
        # Sirf relevant tokens check kar rahe hain (INDENT/DEDENT ko ignore karke)
        actual_tokens = [t for t in tokens if t[0] in {'IDENTIFIER', 'OPERATOR', 'NUMBER'}]

        self.assertEqual(actual_tokens, expected_tokens)

if __name__ == '__main__':
    unittest.main()
