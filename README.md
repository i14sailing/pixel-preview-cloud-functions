
# Generate Pixel-Preview images using Google Cloud Functions 

The idea is to show very pixeled images (without interpolation) until 
the real image is fully loaded.

I got this idea from the [website of the Sanity CMS ](https://www.sanity.io/blog).

###Example 

Original image (~583 KB):

![](examples/tmp-crop.jpg)

<br/>

Pixel-Preview image (1.3KB):~

![](examples/tmp-pixel-lanczos.jpg)


### Which interpolation function?

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

The result with no interpolation looks interesting but might be a bit too much. I am probably going to use lanczos.

