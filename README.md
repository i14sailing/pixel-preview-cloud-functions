
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
