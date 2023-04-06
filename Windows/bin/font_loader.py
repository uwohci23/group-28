# Handles font requests and returns appropriate directory path to parent file
# NOTE: Only returns directory path as STRING and does NOT return FONT data.

bin = 'bin/fonts/'


def load(bold=False, type1=False, type3=False):
    path = bin
    if not type1:
        path += 'New York Hardcore'
    if type3:
        path += 'New York Hardcore'
    if bold:
        path += 'New York Hardcore' if path == bin else '_bold'

    if path == bin:
        path += 'New York Hardcore'

    return path + '.ttf'
