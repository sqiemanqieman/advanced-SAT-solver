from .VSIDS import VSIDS
from .ERWA import ERWA
from .RSR import RSR
from .LRB import LRB
from .CHB import CHB


__all__ = {
    "init_heuristic",
    VSIDS,
    ERWA,
    RSR,
    LRB,
    CHB
}


def init_heuristic(assignment_algorithm, sentence, alpha, discount, batch):
    """Initialize the heuristic."""
    if assignment_algorithm.lower() == 'vsids':
        return VSIDS(sentence, discount)
    elif assignment_algorithm.lower() == 'erwa':
        return ERWA(sentence, alpha)
    elif assignment_algorithm.lower() == 'rsr':
        return RSR(sentence, alpha)
    elif assignment_algorithm.lower() == 'lrb':
        return LRB(sentence, alpha, discount, batch)
    elif assignment_algorithm.lower() == 'chb':
        return CHB(sentence, alpha)
    else:
        raise ValueError('Unknown assignment algorithm: {}'.format(assignment_algorithm))
