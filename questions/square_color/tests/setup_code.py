def to_coordinates(pos: str):
    """description"""
    file, rank = pos
    return ord(file) - ord('a'), ord(rank) - ord('1')