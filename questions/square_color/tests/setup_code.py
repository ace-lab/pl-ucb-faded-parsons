def to_coordinates(pos: str) -> tuple[int, int]:
    """turns a file and rank string (ie 'c3') and turns it into an (int, int)"""
    f_ord, r_ord = tuple(map(ord, pos[:2]))
    return f_ord - ord('a'), r_ord - ord('1')

x = 4