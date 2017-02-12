
def fmt_xpath_spec(tag: str, attributes: dict):
    """Format a xpath_spec string using the given tag and attributes

    The xpath_spec returned is 'absolute', and thus can't be used. Prepend "./" to the xpath spec if using it to
    actually look up an element.

    :param tag: The tag to format into the xpath spec
    :param attributes: The attributes to format into the xpath spec
    :return: An xpath spec string using the given arguments
    """
    if len(attributes) > 0:
        return "{}[{}]".format(tag, ",".join("@{}={}".format(key, value) for key, value in attributes.items()))
    return tag
