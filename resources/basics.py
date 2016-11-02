def dict_setdefault(output, values):
    for key in values:
        if key not in output:
            output[key] = values[key]
