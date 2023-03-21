from .MLR import MLR


__all__ = {
    "init_restart_policy",
}


def init_restart_policy(restart_policy):
    """Initialize the heuristic."""
    if restart_policy is None or restart_policy == "None":
        return None
    elif restart_policy.lower() == 'mlr':
        return MLR()

    else:
        raise ValueError('Unknown restart policy: {}'.format(restart_policy))
