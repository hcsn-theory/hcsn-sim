def momentum_exchange(p1_before, p2_before, p1_after, p2_after, tol=0.1):
    """
    Tests approximate conservation during interaction.
    """
    return abs(
        (p1_before + p2_before) - (p1_after + p2_after)
    ) < tol