
# Generate Pixel-Preview images using Google Cloud Functions 

The idea is to show very pixeled images (without interpolation) until 
the real image is fully loaded.

I got this idea from the [website of the Sanity CMS ](https://www.sanity.io/blog).

<br/>

## Example 

Original image (~583 KB):

![](examples/tmp-crop.jpg)

<br/>

Pixel-Preview image (1.3KB):~

![](examples/tmp-pixel-lanczos.jpg)

<br/>

## Which interpolation function?

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
pixel-preview version of that image should be generate and stored in the same 
directory with an appendix like `-pixel-preview`.

Example: `.../image.jpeg` -> `.../image-pixel-preview.jpeg`

I use a cloud function for that which can be easily "hooked onto" a google 
storage bucket belonging to the same project.

All cloud function endpoints are located within `main.py`. One can test the
implementation locally using `main_text.py` but has to include a valid 
`service-account.json` within the same directory.

<br/>

## Resizing the orignal image?

### Why is a resize necessary? 

If I reduce any image to a fixed width of let's say `64px` the aspect ratios
of the original image an the resulting `64px`-image might differ.

Working with images like `1920x1080`:
* Original: `1920x1080` with aspect ratio `16:9`
* PixelPreview: `64x36` with aspect ratio `16:9`

Not working with images like `3000x2000`:
* Original: `3000x2000` with aspect ratio `3:2`
* PixelPreview: `64x43` (rounded from `64x42.666`) with aspect ratio `64:43 = 2.9767:2`

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

    ratio = size[1]/size[0]
    new_width = size[0]
    new_height = (round(ratio * PIXEL_PREVIEW_WIDTH) / PIXEL_PREVIEW_WIDTH) * size[0]
    
    while round(new_height) != new_height:
        new_width -= 1
        new_height = (math.floor(ratio * PIXEL_PREVIEW_WIDTH) / PIXEL_PREVIEW_WIDTH) * new_width

    return (new_width, int(new_height))
```

I use the function `get_resize_region` to calculate the PixelPreview size.

I use the function `get_crop_region` to calculate the crop 4-tuple 
`(x0, y0, x1, y1)` which crops the image in a centered manner.











