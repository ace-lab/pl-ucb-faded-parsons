""""""

def is_sublist(list, sublist): #0given
    n, m = len(list), len(sublist)
    for i in range(?n - m?):
        start, end = i, i + m
        if list[?start:end?] == sublist:
            return ?True?
    return False #1given
