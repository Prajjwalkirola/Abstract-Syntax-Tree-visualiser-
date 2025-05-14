import unittest
from parser import Parser

class TestParser(unittest.TestCase):
    
    def test_assignment_statement(self):
        # Sample tokens for: x = 5
        tokens = [
            ["IDENTIFIER", "x"],
            ["OPERATOR", "="],
            ["NUMBER", "5"]
        ]

        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = {
            "type": "Program",
            "body": [
                {
                    "type": "Assignment",
                    "name": "x",
                    "value": {"type": "Number", "value": "5"}
                }
            ]
        }

        self.assertEqual(ast, expected_ast)

if __name__ == '__main__':
    unittest.main()
