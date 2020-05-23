
# Generate Pixel-Preview images using Google Cloud Functions 

The idea is to show very pixeled images (without interpolation) until 
the real image is fully loaded.

I got this idea from the [website of the Sanity CMS ](https://www.sanity.io/blog).

<br/>

## Example 

Original image (here: ~583 KB):

![](examples/tmp-crop.jpg)

<br/>

Pixel-Preview image (here: ~1.3KB):

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
pixel-preview version of that image should be generate and stored in the same 
directory with an appendix like `-pixel-preview`.

Example: `.../image.jpeg` -> `.../image-pixel-preview.jpeg`

I use a cloud function for that which can be easily "hooked onto" a google 
storage bucket belonging to the same project.

All cloud function endpoints are located within `main.py`. You can test the
implementation locally using `main_test.py` but has to include a valid 
`service-account.json` from GCP within the same directory.

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
* PixelPreview: `64x42`/`64x43` with aspect ratios `64:42 = 3.0476:2`/`64:43 = 2.9767:2`

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
