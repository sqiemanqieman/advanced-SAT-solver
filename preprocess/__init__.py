from .NiVER import NiVER


__all__ = {
    "init_preprocess_policy"
}


def init_preprocess_policy(preprocess_policy, sentence, num_vars):
    """Preprocess."""
    if preprocess_policy is None or preprocess_policy.lower() == "none":
        return None
    elif preprocess_policy.lower() == 'niver':
        return NiVER(sentence, num_vars, True)
    elif preprocess_policy.lower() == 'lighter-niver':
        return NiVER(sentence, num_vars, False)
    elif preprocess_policy.lower() == 'li-niver-withple':
        return NiVER(sentence, num_vars, False, True)
    else:
        raise ValueError('Unknown preprocess policy: {}'.format(preprocess_policy))
