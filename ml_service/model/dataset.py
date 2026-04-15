LABELS = ["Syntax Error", "Runtime Error", "Logic Bug", "Multiple Issues"]

RAW_DATA = [
    # SYNTAX ERRORS
    {"code": "def greet(name)\n    print('Hello, ' + name)", "label": 0},
    {"code": "for i in range(10)\n    print(i)", "label": 0},
    {"code": "if x > 0\n    print('pos')\nelse:\n    print('neg')", "label": 0},
    {"code": "class Dog:\n    def __init__(self, name:\n        self.name = name", "label": 0},
    {"code": "def add(a, b):\nreturn a + b", "label": 0},
    {"code": "x = (1 + 2\ny = x * 3", "label": 0},
    {"code": "print('Hello World'", "label": 0},
    {"code": "nums = [1, 2, 3\nprint(nums)", "label": 0},
    {"code": "def divide(a, b):\n   if b != 0:\n  return a / b", "label": 0},
    {"code": "def factorial(n):\n    if n == 0\n        return 1\n    return n * factorial(n-1)", "label": 0},
    {"code": "numbers = [1, 2, 3]\nprint(numbers[10])", "label": 1},
    {"code": "x = 10\ny = 0\nresult = x / y", "label": 1},
    {"code": "name = 'Alice'\nprint(name + 42)", "label": 1},
    {"code": "def greet():\n    print(message)\n\ngreet()", "label": 1},
    {"code": "data = {'name': 'Alice'}\nprint(data['age'])", "label": 1},
    {"code": "text = None\nprint(text.upper())", "label": 1},
    {"code": "import maths\nprint(maths.sqrt(16))", "label": 1},
    {"code": "items = (1, 2, 3)\nitems[0] = 99", "label": 1},
    {"code": "stack = []\nprint(stack.pop())", "label": 1},
    {"code": "def process(data):\n    return data['value'] * 2\n\nprocess(None)", "label": 1},
    {"code": "def is_even(n):\n    return n % 2 == 1", "label": 2},
    {"code": "def is_palindrome(s):\n    return s == s[::-0]", "label": 2},
    {"code": "def celsius_to_fahrenheit(c):\n    return c * 9 / 5 - 32", "label": 2},
    {"code": "def count_vowels(s):\n    count = 0\n    for ch in s:\n        if ch in 'aeiou':\n            count += 1\n    return count - 1", "label": 2},
    {"code": "def max_of_three(a, b, c):\n    if a > b and a > c:\n        return b\n    elif b > c:\n        return b\n    return c", "label": 2},
    {"code": "total = 0\nfor i in range(1, 10):\n    total += i\nprint(total)", "label": 2},
    {"code": "def average(nums):\n    return sum(nums) / len(nums) + 1", "label": 2},
    {"code": "def celsius_to_kelvin(c):\n    return c - 273.15", "label": 2},
    {"code": "def binary_search(arr, t):\n    lo, hi = 0, len(arr)\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == t: return mid\n        elif arr[mid] < t: lo = mid\n        else: hi = mid - 1\n    return -1", "label": 2},
    {"code": "def fizzbuzz(n):\n    for i in range(n):\n        if i % 15 == 0: print('FizzBuzz')\n        elif i % 3 == 0: print('Fizz')\n        elif i % 5 == 0: print('Buzz')\n        else: print(i)", "label": 2},
    {"code": "def factorial(n)\n    if n = 0:\n        return 1\n    return n * factorial(n-1)", "label": 3},
    {"code": "def divide_list(nums, d):\n    results = []\n    for i in range(len(nums) + 1):\n        results.append(nums[i] / d)\n    return results\n\ndivide_list([1,2,3], 0)", "label": 3},
    {"code": "class Stack\n    def __init__(self):\n        self.items = ()\n\n    def push(self, item):\n        self.items.append(item)", "label": 3},
    {"code": "import syss\n\ndef read_file(path)\n    with open(path) as f\n        return f.read()", "label": 3},
    {"code": "def merge(a, b):\n    result = []\n    i = j = 0\n    while i < len(a) or j < len(b):\n        if a[i] < b[j]:\n            result.append(a[i])\n            i =+ 1\n        else:\n            result.append(b[j])\n            j =+ 1\n    return result", "label": 3},
]

def get_dataset():
    return RAW_DATA

def get_full_dataset(generated) :
    """Merges handcrafted + Groq-generated examples."""
    return RAW_DATA + generated
