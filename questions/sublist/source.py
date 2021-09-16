""" Make a function <code>is_sublist</code> that checks whether the first
    argument contains the second as a sublist (including ordering), eg

    <pl-code language="python">
    >> is_sublist(['a', 'b', 'c', 'd'], ['b', 'c'])
    True
    >> is_sublist([1, 2, 3, 4], [4, 3])
    False</pl-code>
"""

def is_sublist(list, sublist):
    n, m = len(list), len(sublist)
    for i in range(n - m):
        start, end = i, i + m
        if list[start:end] == sublist:
            return True
    return False
