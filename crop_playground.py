
import math
import random
import time

def get_snap_size(size):
    # size given as a (width, height) 2-tuple

    if suffices_pixel_ratio(size):
        return size

    prev_cutoff = 0
    current_cutoff = 10

    while (prev_cutoff < size[0] and prev_cutoff < size[1]):

        size_options = get_crop_size_options(
            size,
            cutoff=current_cutoff,
            prev_cutoff=prev_cutoff)

        for size_option in size_options:
            if suffices_pixel_ratio(size_option):
                return size_option

        current_cutoff += 10
        prev_cutoff += 10

    return (0, 0)



def get_crop_size_options(size, cutoff=10, prev_cutoff=0):
    # size given as a (width, height) 2-tuple
    sizes = []

    from_width = size[0] - prev_cutoff
    to_width = size[0] - cutoff

    from_height = size[1] - prev_cutoff
    to_height = size[1] - cutoff

    """
    XXX CCC
    XXX CCC
    AAA BBB
    AAA BBB
    """
    # X = Already checked

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

    sizes.sort(key=lambda x: x[2], reverse=True)
    return sizes


def suffices_pixel_ratio(size, pixel_width=64):
    # size given as a (width, height) 2-tuple
    scaling_factor = pixel_width/size[0]
    pixel_height = scaling_factor * size[1]
    return int(pixel_height) == pixel_height




PIXEL_PREVIEW_WIDTH = 64

def get_snap_size_old(size):
    # size given as (width, height) 2-tuple
    crop_width = size[0]
    crop_height = size[1]

    # 1) Calculated floored height of the pixel image (may differ in aspect ratio)
    pixel_height = math.floor(PIXEL_PREVIEW_WIDTH * (crop_height/crop_width))

    # 2) Calculated full height with the pixel-image-ratio
    crop_height = (pixel_height/PIXEL_PREVIEW_WIDTH) * crop_width

    # 3) When that full height is a whole number -> finished
    while int(crop_height) != crop_height:
        crop_width -= 1
        pixel_height = math.floor(PIXEL_PREVIEW_WIDTH * (crop_height / crop_width))
        crop_height = (pixel_height / PIXEL_PREVIEW_WIDTH) * crop_width

    # The resulting image will have an aspect ratio of 64:1 or 64:2 ... 64:100 or 64:101 ...

    # A way better version of this Algorithm would be if it would sequentially test the
    # crop sizes ordered by how many pixels of the image would be lost!

    return (crop_width, int(crop_height))


if __name__ == '__main__':
    t1 = time.time()
    for i in range(1000):
        # sizes = get_crop_size_options((300, 200))
        pass
    t2 = time.time()
    # way less than 1ms for cutoff=40 -> not a very
    # elegant solution but the computational effort
    # is moderate. whether each size suffices any
    # pixel-aspect-ration must be checked anyway



    # FULL TEST

    old_time = 0
    new_time = 0
    old_reduction = 0
    new_reduction = 0

    n_tests = 100000

    samples = []
    for i in range(n_tests):
        w = random.randrange(400, 4000)
        h = random.randrange(250, 2500)
        full_area = w * h
        samples.append([w, h, full_area, 0, 0])

    t1 = time.time()
    for i in range(n_tests):
        size = get_snap_size_old((samples[i][0], samples[i][1]))
        samples[i][3] = size[0] * size[1]
    old_time = (time.time() - t1)/n_tests

    t2 = time.time()
    for i in range(n_tests):
        size = get_snap_size((samples[i][0], samples[i][1]))
        samples[i][4] = size[0] * size[1]
    new_time = (time.time() - t2)/n_tests

    old_avg_reduction = 0
    new_avg_reduction = 0
    for i in range(n_tests):
        old_avg_reduction += (samples[i][3] - samples[i][2])/samples[i][2]
        new_avg_reduction += (samples[i][4] - samples[i][2])/samples[i][2]
    old_avg_reduction /= n_tests
    new_avg_reduction /= n_tests

    print(f"old_avg_reduction = {round(old_avg_reduction*100, 3)}%")
    print(f"new_avg_reduction = {round(new_avg_reduction*100, 3)}%")
    print(f"old_time = {round(old_time*1000, 6)}ms")
    print(f"new_time = {round(new_time*1000, 6)}ms")

