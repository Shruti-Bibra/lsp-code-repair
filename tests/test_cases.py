# Test cases for code evaluation
TEST_CASES = [
    {
        "name": "Correct, complete code",
        "code": b"import os\n\ndef my_func():\n    return os.getcwd()",
        "expected_score": 0.0,
    },
    {
        "name": "Code with an undefined variable error",
        "code": b"def my_func():\n    print(undeclared_variable)",
        "expected_score": float("-inf"),
    },
    {
        "name": "Incomplete code (open function signature)",
        "code": b"def my_func(",
        "expected_score": 0.0,
    },
    {
        "name": "Incomplete code (if statement with no body)",
        "code": b"def my_func(x):\n    if x > 10:",
        "expected_score": 0.0,
    },
    {
        "name": "Syntactically valid code with a type error",
        "code": b"def add(a: int, b: int) -> int:\n    return 'hello'",
        "expected_score": float("-inf"),
    },
    {
        "name": "Empty code",
        "code": b"",
        "expected_score": 0.0,
    },
    {
        "name": "Code with only whitespace",
        "code": b"    \n  ",
        "expected_score": 0.0,
    },
    {
        "name": "Code importing a non-existent module",
        "code": b"import a_module_that_does_not_exist",
        "expected_score": float("-inf"),
    },
]
