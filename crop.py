
def get_snap_size(size):
    # size given as a (width, height) 2-tuple

    prev_cutoff = 0
    current_cutoff = 10

    while (prev_cutoff < size[0] and prev_cutoff < size[1]):

        size_options = get_crop_size_options(
            size,
            cutoff=current_cutoff,
            prev_cutoff=prev_cutoff)

        for size_option in size_options:
            if suffices_pixel_ratio(size_option):
                return (size_option[0], size_option[1])

        current_cutoff += 10
        prev_cutoff += 10

    return (0, 0)


def get_crop_size_options(size, cutoff=10, prev_cutoff=0):
    # size given as a (width, height) 2-tuple

    # Generate all possible image_crop_sizes width both dx
    # and dy less than the cutoff value

    # prev_cutoff can be used when this function is called
    # multiple times when the first options list did not
    # contain a match.

    # X = Already checked
    # prev_cutoff = width/height of the X region
    # cutoff = width/height of the full region
    """
    XXX CCC
    XXX CCC
    AAA BBB
    AAA BBB
    """

    sizes = []

    from_width = size[0] - prev_cutoff
    to_width = size[0] - cutoff

    from_height = size[1] - prev_cutoff
    to_height = size[1] - cutoff

    # Regions A + B
    for w in range(size[0], to_width, -1):
        for h in range(from_height, to_height, -1):
            if h == 0:
                break
            sizes.append((w, h, w*h))

    # Regions C
    for w in range(from_width, to_width, -1):
        if w == 0:
            break
        for h in range(size[1], from_height, -1):
            if h == 0:
                break
            sizes.append((w, h, w*h))
            # It is less memory efficient to store the area
            # in the tuple but ~ 30% faster when sorting in
            # comparison to calculating it during sorting
            # with "key=lambda x: x[0]*x[1]"

    sizes.sort(key=lambda x: x[2], reverse=True)
    return sizes


def suffices_pixel_ratio(size, pixel_width=64):
    # size given as a (width, height) 2-tuple
    scaling_factor = pixel_width/size[0]
    pixel_height = scaling_factor * size[1]
    return int(pixel_height) == pixel_height
