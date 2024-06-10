from yarl import URL


def get_url_from_args(arguments: tuple) -> URL | str:
    for arg in arguments:
        if isinstance(arg, URL):
            return arg

    return "<unknown URL>"
