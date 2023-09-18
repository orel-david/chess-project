class NonLegal(Exception):
    """
    Exception for an illegal move.
    """
    pass


class KingNonLegal(Exception):
    """
    Exception for a move that doesn't protect that is illegal for the king.
    """
    pass


class KingUnderCheck(Exception):
    """
    Exception to when the king is under check but isn't protected by the move.
    """
    pass


class KingSacrifice(Exception):
    """
    Exception for a move that sacrifices the king.
    """
    pass
