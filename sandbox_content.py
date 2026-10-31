"""Built-in problem bank for the Coding Sandbox.

Each problem carries starter code, a reference solution, hints and real test
cases. Test cases are executed by sandbox_runner.py.
"""

PROBLEMS = [
    {
        'slug': 'two-sum',
        'title': 'Two Sum',
        'difficulty': 'Easy',
        'category': 'Arrays',
        'description': (
            'Given an array of integers nums and an integer target, return the indices of '
            'the two numbers that add up to target.\n\n'
            'You may assume that each input has exactly one solution, and you may not use '
            'the same element twice. Return the answer in any order.\n\n'
            'Example 1: nums = [2, 7, 11, 15], target = 9 -> [0, 1]\n'
            'Example 2: nums = [3, 2, 4], target = 6 -> [1, 2]\n'
            'Example 3: nums = [3, 3], target = 6 -> [0, 1]'
        ),
        'function_name': 'two_sum',
        'function_name_js': 'twoSum',
        'starter_code': (
            'def two_sum(nums, target):\n'
            '    # Write your solution here\n'
            '    pass\n\n'
            '# Sample run\n'
            'print(two_sum([2, 7, 11, 15], 9))'
        ),
        'starter_code_js': (
            'function twoSum(nums, target) {\n'
            '    // Write your solution here\n'
            '}\n\n'
            '// Sample run\n'
            'console.log(twoSum([2, 7, 11, 15], 9));'
        ),
        'solution_code': (
            'def two_sum(nums, target):\n'
            '    seen = {}\n'
            '    for i, num in enumerate(nums):\n'
            '        need = target - num\n'
            '        if need in seen:\n'
            '            return [seen[need], i]\n'
            '        seen[num] = i\n'
            '    return []'
        ),
        'solution_code_js': (
            'function twoSum(nums, target) {\n'
            '    const seen = new Map();\n'
            '    for (let i = 0; i < nums.length; i++) {\n'
            '        const need = target - nums[i];\n'
            '        if (seen.has(need)) return [seen.get(need), i];\n'
            '        seen.set(nums[i], i);\n'
            '    }\n'
            '    return [];\n'
            '}'
        ),
        'hints': [
            'For every number, check whether target - number has already been seen.',
            'A dictionary/hash map stores value -> index, so each lookup is O(1).',
            "If no pair exists, return an empty list. The answer can be in any order.",
        ],
        'test_cases': [
            {'args': [[2, 7, 11, 15], 9], 'expected': [0, 1]},
            {'args': [[3, 2, 4], 6], 'expected': [1, 2]},
            {'args': [[3, 3], 6], 'expected': [0, 1]},
            {'args': [[-1, -2, -3, -4, -5], -8], 'expected': [2, 4]},
        ],
        'time_limit_minutes': 30,
    },
    {
        'slug': 'reverse-string',
        'title': 'Reverse String',
        'difficulty': 'Easy',
        'category': 'Strings',
        'description': (
            'Given a string s, return the string reversed.\n\n'
            'Example 1: s = "hello" -> "olleh"\n'
            'Example 2: s = "RecruitPro" -> "orPtiurceR"\n'
            'Example 3: s = "" -> ""'
        ),
        'function_name': 'reverse_string',
        'function_name_js': 'reverseString',
        'starter_code': (
            'def reverse_string(s):\n'
            '    # Write your solution here\n'
            '    pass\n\n'
            '# Sample run\n'
            'print(reverse_string("hello"))'
        ),
        'starter_code_js': (
            'function reverseString(s) {\n'
            '    // Write your solution here\n'
            '}\n\n'
            '// Sample run\n'
            'console.log(reverseString("hello"));'
        ),
        'solution_code': (
            'def reverse_string(s):\n'
            '    return s[::-1]'
        ),
        'solution_code_js': (
            'function reverseString(s) {\n'
            "    return s.split('').reverse().join('');\n"
            '}'
        ),
        'hints': [
            'Python strings support slicing: s[start:stop:step].',
            'A step of -1 walks the string backwards.',
            'Empty strings and single characters are already reversed.',
        ],
        'test_cases': [
            {'args': ['hello'], 'expected': 'olleh'},
            {'args': [''], 'expected': ''},
            {'args': ['RecruitPro'], 'expected': 'orPtiurceR'},
            {'args': ['a'], 'expected': 'a'},
        ],
        'time_limit_minutes': 15,
    },
    {
        'slug': 'fizzbuzz',
        'title': 'FizzBuzz',
        'difficulty': 'Easy',
        'category': 'Math',
        'description': (
            'Given an integer n, return a list of strings from 1 to n where:\n\n'
            '- "FizzBuzz" if the number is divisible by both 3 and 5\n'
            '- "Fizz" if divisible by 3\n'
            '- "Buzz" if divisible by 5\n'
            '- otherwise the number as a string\n\n'
            'Example: n = 5 -> ["1", "2", "Fizz", "4", "Buzz"]'
        ),
        'function_name': 'fizzbuzz',
        'function_name_js': 'fizzBuzz',
        'starter_code': (
            'def fizzbuzz(n):\n'
            '    # Write your solution here\n'
            '    pass\n\n'
            '# Sample run\n'
            'print(fizzbuzz(5))'
        ),
        'starter_code_js': (
            'function fizzBuzz(n) {\n'
            '    // Write your solution here\n'
            '}\n\n'
            '// Sample run\n'
            'console.log(fizzBuzz(5));'
        ),
        'solution_code': (
            'def fizzbuzz(n):\n'
            '    out = []\n'
            '    for i in range(1, n + 1):\n'
            '        if i % 15 == 0:\n'
            "            out.append('FizzBuzz')\n"
            '        elif i % 3 == 0:\n'
            "            out.append('Fizz')\n"
            '        elif i % 5 == 0:\n'
            "            out.append('Buzz')\n"
            '        else:\n'
            '            out.append(str(i))\n'
            '    return out'
        ),
        'solution_code_js': (
            'function fizzBuzz(n) {\n'
            '    const out = [];\n'
            '    for (let i = 1; i <= n; i++) {\n'
            '        if (i % 15 === 0) out.push("FizzBuzz");\n'
            '        else if (i % 3 === 0) out.push("Fizz");\n'
            '        else if (i % 5 === 0) out.push("Buzz");\n'
            '        else out.push(String(i));\n'
            '    }\n'
            '    return out;\n'
            '}'
        ),
        'hints': [
            'Check divisibility by 15 first, otherwise 15 would print "Fizz" only.',
            'Use the modulo operator (%) to test divisibility.',
            'Remember to convert ordinary numbers to strings.',
        ],
        'test_cases': [
            {'args': [3], 'expected': ['1', '2', 'Fizz']},
            {'args': [5], 'expected': ['1', '2', 'Fizz', '4', 'Buzz']},
            {'args': [1], 'expected': ['1']},
            {'args': [15], 'expected': [
                '1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz',
                '11', 'Fizz', '13', '14', 'FizzBuzz',
            ]},
        ],
        'time_limit_minutes': 15,
    },
    {
        'slug': 'valid-parentheses',
        'title': 'Valid Parentheses',
        'difficulty': 'Medium',
        'category': 'Stack',
        'description': (
            'Given a string s containing only the characters ( ) [ ] { }, determine if the '
            'brackets are valid.\n\n'
            'Brackets are valid when every opening bracket is closed by the same type of '
            'bracket and they close in the correct order.\n\n'
            'Example 1: s = "()[]{}" -> true\n'
            'Example 2: s = "(]" -> false\n'
            'Example 3: s = "{[]}" -> true'
        ),
        'function_name': 'is_valid',
        'function_name_js': 'isValid',
        'starter_code': (
            'def is_valid(s):\n'
            '    # Write your solution here\n'
            '    pass\n\n'
            '# Sample run\n'
            'print(is_valid("()[]{}"))'
        ),
        'starter_code_js': (
            'function isValid(s) {\n'
            '    // Write your solution here\n'
            '}\n\n'
            '// Sample run\n'
            'console.log(isValid("()[]{}"));'
        ),
        'solution_code': (
            'def is_valid(s):\n'
            '    pairs = {")": "(", "]": "[", "}": "{"}\n'
            '    stack = []\n'
            '    for ch in s:\n'
            '        if ch in "([{":\n'
            '            stack.append(ch)\n'
            '        elif not stack or stack.pop() != pairs.get(ch):\n'
            '            return False\n'
            '    return not stack'
        ),
        'solution_code_js': (
            'function isValid(s) {\n'
            '    const pairs = {")": "(", "]": "[", "}": "{"};\n'
            '    const stack = [];\n'
            '    for (const ch of s) {\n'
            '        if (ch === "(" || ch === "[" || ch === "{") {\n'
            '            stack.push(ch);\n'
            '        } else if (stack.pop() !== pairs[ch]) {\n'
            '            return false;\n'
            '        }\n'
            '    }\n'
            '    return stack.length === 0;\n'
            '}'
        ),
        'hints': [
            'Use a stack: push every opening bracket.',
            'When you see a closing bracket, pop and compare with the expected opener.',
            'The string is valid only if the stack is empty at the end.',
        ],
        'test_cases': [
            {'args': ['()'], 'expected': True},
            {'args': ['()[]{}'], 'expected': True},
            {'args': ['(]'], 'expected': False},
            {'args': ['([)]'], 'expected': False},
            {'args': ['{[]}'], 'expected': True},
        ],
        'time_limit_minutes': 25,
    },
    {
        'slug': 'maximum-subarray',
        'title': 'Maximum Subarray',
        'difficulty': 'Medium',
        'category': 'Dynamic Programming',
        'description': (
            'Given an integer array nums, find the contiguous subarray with the largest sum '
            'and return that sum.\n\n'
            'Example 1: nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4] -> 6\n'
            'Explanation: [4, -1, 2, 1] has the largest sum = 6.\n'
            'Example 2: nums = [1] -> 1\n'
            'Example 3: nums = [5, 4, -1, 7, 8] -> 23'
        ),
        'function_name': 'max_subarray',
        'function_name_js': 'maxSubArray',
        'starter_code': (
            'def max_subarray(nums):\n'
            '    # Write your solution here\n'
            '    pass\n\n'
            '# Sample run\n'
            'print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))'
        ),
        'starter_code_js': (
            'function maxSubArray(nums) {\n'
            '    // Write your solution here\n'
            '}\n\n'
            '// Sample run\n'
            'console.log(maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4]));'
        ),
        'solution_code': (
            'def max_subarray(nums):\n'
            '    best = current = nums[0]\n'
            '    for n in nums[1:]:\n'
            '        current = max(n, current + n)\n'
            '        best = max(best, current)\n'
            '    return best'
        ),
        'solution_code_js': (
            'function maxSubArray(nums) {\n'
            '    let best = nums[0], current = nums[0];\n'
            '    for (let i = 1; i < nums.length; i++) {\n'
            '        current = Math.max(nums[i], current + nums[i]);\n'
            '        best = Math.max(best, current);\n'
            '    }\n'
            '    return best;\n'
            '}'
        ),
        'hints': [
            'At every position decide: extend the previous subarray or start fresh here?',
            "Kadane's algorithm keeps a running sum and the best sum seen so far.",
            'All-negative arrays are valid input, so initialise with the first element.',
        ],
        'test_cases': [
            {'args': [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], 'expected': 6},
            {'args': [[1]], 'expected': 1},
            {'args': [[5, 4, -1, 7, 8]], 'expected': 23},
            {'args': [[-3, -1, -2]], 'expected': -1},
        ],
        'time_limit_minutes': 30,
    },
    {
        'slug': 'longest-common-prefix',
        'title': 'Longest Common Prefix',
        'difficulty': 'Easy',
        'category': 'Strings',
        'description': (
            'Given a list of strings, return the longest common prefix shared by all of them. '
            'If there is no common prefix, return an empty string.\n\n'
            'Example 1: ["flower", "flow", "flight"] -> "fl"\n'
            'Example 2: ["dog", "racecar", "car"] -> ""\n'
            'Example 3: ["interview", "internet", "internal"] -> "inter"'
        ),
        'function_name': 'longest_common_prefix',
        'function_name_js': 'longestCommonPrefix',
        'starter_code': (
            'def longest_common_prefix(strs):\n'
            '    # Write your solution here\n'
            '    pass\n\n'
            '# Sample run\n'
            'print(longest_common_prefix(["flower", "flow", "flight"]))'
        ),
        'starter_code_js': (
            'function longestCommonPrefix(strs) {\n'
            '    // Write your solution here\n'
            '}\n\n'
            '// Sample run\n'
            'console.log(longestCommonPrefix(["flower", "flow", "flight"]));'
        ),
        'solution_code': (
            'def longest_common_prefix(strs):\n'
            "    if not strs:\n        return ''\n"
            '    prefix = strs[0]\n'
            '    for s in strs[1:]:\n'
            '        while not s.startswith(prefix):\n'
            '            prefix = prefix[:-1]\n'
            "            if not prefix:\n                return ''\n"
            '    return prefix'
        ),
        'solution_code_js': (
            'function longestCommonPrefix(strs) {\n'
            "    if (!strs.length) return '';\n"
            '    let prefix = strs[0];\n'
            '    for (const s of strs.slice(1)) {\n'
            '        while (!s.startsWith(prefix)) {\n'
            '            prefix = prefix.slice(0, -1);\n'
            "            if (!prefix) return '';\n"
            '        }\n'
            '    }\n'
            '    return prefix;\n'
            '}'
        ),
        'hints': [
            'Start with the first word as the candidate prefix.',
            'Shrink the prefix until every other word starts with it.',
            'If the prefix becomes empty, the answer is an empty string.',
        ],
        'test_cases': [
            {'args': [['flower', 'flow', 'flight']], 'expected': 'fl'},
            {'args': [['dog', 'racecar', 'car']], 'expected': ''},
            {'args': [['interview', 'internet', 'internal']], 'expected': 'inter'},
            {'args': [['a']], 'expected': 'a'},
        ],
        'time_limit_minutes': 20,
    },
]
