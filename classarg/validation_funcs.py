def _collect_bool_args(spec, matcher):
    bool_args = set()
    for name, value in matcher.items():
        if isinstance(value, bool):
            bool_args.add(name)

    return bool_args


def at_least(*flag_names, spec, matcher):
    bool_args = _collect_bool_args(spec, matcher)

    for flag in flag_names:
        if flag not in matcher:
            raise KeyError(
                "Flag '{0}' not found in spec or input".format(flag))

        if flag not in bool_args:
            raise TypeError(("Expect '{0}' to be boolean type"
                             "but receive {1} instead.").format(
                                 flag, type(matcher[flag])))

    if all(matcher[flag] is False for flag in flag_names):
        raise ValueError(
            "At least one of the following flags"
            "should be set to True: {}".format(flag_names))


def one_of(*flag_names, spec, matcher):
    pass


def enforce_type(mode, *, spec, matcher):
    """mode: one of 'error', 'str'"""
    pass
