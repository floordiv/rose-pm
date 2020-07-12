def split_by_quotes(line, on_line='null'):
    result = ['']
    temp = []
    in_string = False

    for letter in line:
        if letter == '"':
            temp += [letter]

            if in_string:
                result += [''.join(temp), '']
                temp = []
                in_string = False
            else:
                in_string = True

        elif in_string:
            temp += [letter]
        else:
            result[-1] += letter

    return list(filter(lambda _element: _element != '', result))


def split(line, split_by=' ', on_line='null'):
    result = ['']
    line = remove_comments(line)

    for element in split_by_quotes(line, on_line=on_line):
        if element[0] == '"':
            result += [element, '']
        else:
            for letter in element.strip():
                if letter == split_by:
                    result += ['']
                else:
                    result[-1] += letter

    return list(filter(lambda _element: _element != '', result))


def remove_comments(line):
    in_string = False

    for index, letter in enumerate(line):
        if letter == '"':
            in_string = not in_string
        elif not in_string and letter == ';':
            return line[:index]

    return line


def parse_args(args):
    split_args = split(args)
    args, kwargs = [], {}
    next_arg_is_value = False

    for arg in split_args:
        if next_arg_is_value:
            arg = arg.strip('"')
            kwargs[next_arg_is_value] = arg
            next_arg_is_value = False
        elif arg[0] == '"':
            args += [arg[1:-1]]
        else:
            if arg[-1] == '=':
                next_arg_is_value = arg[:-1]
            elif '=' in arg:
                var, *val = arg.split('=')
                kwargs[var] = val
            else:
                args += [arg]

    return args, kwargs


def parse(args, template, only_args=False, only_kwargs=False):
    if isinstance(list, args):
        args = " ".join(args)

    args, kwargs = parse_args(args)

    if only_args:
        return list(set(template + args))
    if only_kwargs:
        return {**template, **kwargs}

    return args, kwargs
