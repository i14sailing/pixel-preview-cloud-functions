
# Generate Pixel-Preview images using Google Cloud Functions 

The idea is to show very low res images, e.g. 64px wide, BUT: without interpolation, until 
the real image is fully loaded.

I got this idea from the [website of the Sanity CMS ](https://www.sanity.io/blog). But they don't use it anymore :/

<br/>

## Example 

Original image (here: ~583 KB):

![](examples/tmp-crop.jpg)

<br/>

PixelPreview image (here: ~1.3KB):

![](examples/tmp-pixel-lanczos.jpg)

<br/>

## Which downsampling function?

No interpolation/Nearest (here: ~1,6KB):

![](examples/tmp-pixel-nearest.jpg)

<br/>

Bilinear (here: ~1,3KB):

![](examples/tmp-pixel-bilinear.jpg)

<br/>

Bicubic (here: ~1,3KB):

![](examples/tmp-pixel-bicubic.jpg)

<br/>

Lanczos (here: ~1,3KB):

![](examples/tmp-pixel-lanczos.jpg)

<br/>

The result with no interpolation looks interesting but might be a bit too much.

I am probably going to use lanczos.

<br/>

## Google Cloud Functions

Goal: Every time a new image is uploaded or an existing image is modified a 
PixelPreview version of that image should be generated and stored in the same 
directory with an appendix like `-pixel-preview`.

Example: `.../image.jpeg` -> `.../image-pixel-preview.jpeg`

I use a cloud function for that which can be easily "hooked onto" a google 
storage bucket belonging to the same project.

All cloud function endpoints are located within `main.py`. You can test the
implementation locally using `main_test.py` but have to include a valid 
`service-account.json` from GCP within the same directory.

<br/>

## Resizing the orignal image?

### Why is a resize necessary? 

If I reduce any image to a fixed width of let's say `64px` the aspect ratios
of the original image an the resulting `64px`-image might differ.

No problem with images like `1920x1080`:
* Original: `1920x1080` with aspect ratio `16:9`
* PixelPreview: `64x36` with aspect ratio `16:9`

Problematic with images like `3000x2000`:
* Original: `3000x2000` with aspect ratio `3:2`
* PixelPreview: `64x42` or `64x43` with aspect ratios `3.0476:2` or `2.9767:2` respectively

<br/>

Idea: Not only generate the PixelPreview but also replace the original image 
with a cropped version if needed.

<br/>

### Implementation

Calculating the cropped size that suffices a given `PIXEL_PREVIEW_WIDTH`:

```python
import math

PIXEL_PREVIEW_WIDTH = 64

def get_snap_size(size):
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

    return (crop_width, int(crop_height))
```

I use the function `get_resize_region` to calculate the PixelPreview size.

I use the function `get_crop_region` to calculate the crop 4-tuple 
`(x0, y0, x1, y1)` which crops the image in a centered manner.

<br/>

### Improving the "get_snap_size"-Algorithm

A way better variant of this Algorithm would be a version that sequentially tested the 
crop sizes ordered by how many pixels of the image would be lost! That way the algorithm 
will always produce the cropped size with the least possible lost image area.

<br/>

First I need the possible crops sorted descendingly by cropped area: `[(3000, 2000), 
(2999, 2000), (3000, 1999), (2998, 2000), (2999, 1999), (3000, 1998), (2997, 2000), 
(2998, 1999), ...]`.

To be honest I did not figure out yet how to implement this way of counting downwards
in code in an efficient way.

So I just implemented a function generating all of these possible sizes up to a certain
`cutoff` value (`dx,dy < cutoff`) and sorting them: `get_crop_size_options` in `crop.py`.

This function also supports passing it the cutoff from the previous options-list called
`prev_cutoff` so that no options will be checked duplicately.

<br/>

The function `suffices_pixel_ratio` just checks whether the PixelPreview of an image has
the same aspect ratio as the original image:

```python
def suffices_pixel_ratio(size, pixel_width=64):
    # size given as a (width, height) 2-tuple
    scaling_factor = pixel_width/size[0]
    pixel_height = scaling_factor * size[1]
    return int(pixel_height) == pixel_height
```

<br/>

The new version of the algorithm is certainly easier to understand:

```python
def get_snap_size(size):
    # size given as a (width, height) 2-tuple

    if suffices_pixel_ratio(size):
        return size

    prev_cutoff = 0
    current_cutoff = 10

    while (prev_cutoff < max(size)):

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
```

### A word on Performance

This new version takes significantly longer than the old one. In `crop_playground.py` 
you can see how I compared their performance. For a large amount of images I would 
probably store these computations.

*Test samples (not super representativ): 100.000 random image sizes with width in 
`[400, 4000[` and height in `[250, 2500[` .*

<br/>

Average performance of the **old** algorithm:
* Loss of image area: `~ 4.34%`
* Time taken: `~ 0.0124ms`

Average performance of the **new** algorithm:
* Loss of image area: `~ 2.56%` *(optimal)*
* Time taken: `~ 0.701ms`

So way less loss of image area but about 57 times slower ...

<br/>

What to to about it? Right now, nothing! Why? When taking into account what the rest 
of the program does it is obvious that +0.7ms/image is not a big issue compared to the 
rest. 

Opening a locally stored image with `PIL` and storing a cropped version of it takes 
`> 120ms` on the same hardware. In addition to that I am fetching the source image 
from a storage bucket as well as write into a storage bucket two times (in case the 
image has to be cropped).

So optimization could definitely be relevant in another setup but not here.

<br/>

## Wrapping the PixelPreview in a React Component

The goal is to have a React component `PixelImagePreview` that updates 
really fast with the `src` of the preview image and loads the actual 
image after it has been mounted. The desired result: For the 
loading time the pixel preview image is visible.

![](examples/PixelImagePreview.gif)

For the top white part of these slideshow images the chosen downsampling 
function lanczos is not ideal! I will have to look for a better one here.

<br/>

## Some Side Notes

*There is probably a better way to asynchronously load 
images with JS after the placeholder `<img>` tag has been mounted in
the DOM. Message me if you want to tell me how to improve the 
implementation ;)*

*I am using images for this slideshow instead of a pdf because every 
js/react pdf library I tried out had a significant bundle size as well 
as way more runtime overhead than using plain images. In addition to 
that I am using  the same image slider on the whole page (blog-posts, 
gallery, slideshows) so if I were to use a pdf then I would have to 
build a more logic for the  pdf slider.*
