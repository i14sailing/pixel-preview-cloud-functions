
# Generate Pixel-Preview images using Google Cloud Functions 

The idea is to show very pixeled images (without interpolation) until 
the real image is fully loaded.

I got this idea from the [website of the Sanity CMS ](https://www.sanity.io/blog).

###Example 

Original image (~583 KB):

![](examples/tmp-crop.jpg)

<br/>

Pixel-Preview image (1.3KB):~

<img style="width: 100%; image-rendering: optimizeSpeed; image-rendering: -moz-crisp-edges; image-rendering: -o-crisp-edges; image-rendering: -webkit-optimize-contrast; image-rendering: pixelated; image-rendering: optimize-contrast; -ms-interpolation-mode: nearest-neighbor;" src="examples/tmp-pixel-lanczos.jpg"/>


### Which interpolation function?

No interpolation/Nearest (here: ~1,6KB):

<img style="width: 50%; display: block; image-rendering: optimizeSpeed; image-rendering: -moz-crisp-edges; image-rendering: -o-crisp-edges; image-rendering: -webkit-optimize-contrast; image-rendering: pixelated; image-rendering: optimize-contrast; -ms-interpolation-mode: nearest-neighbor;" src="examples/tmp-pixel-nearest.jpg"/>

<br/>

Bilinear (here: ~1,3KB):

<img style="width: 50%; display: block; image-rendering: optimizeSpeed; image-rendering: -moz-crisp-edges; image-rendering: -o-crisp-edges; image-rendering: -webkit-optimize-contrast; image-rendering: pixelated; image-rendering: optimize-contrast; -ms-interpolation-mode: nearest-neighbor;" src="examples/tmp-pixel-bilinear.jpg"/>

<br/>

Bicubic (here: ~1,3KB):

<img style="width: 50%; display: block; image-rendering: optimizeSpeed; image-rendering: -moz-crisp-edges; image-rendering: -o-crisp-edges; image-rendering: -webkit-optimize-contrast; image-rendering: pixelated; image-rendering: optimize-contrast; -ms-interpolation-mode: nearest-neighbor;" src="examples/tmp-pixel-bicubic.jpg"/>

<br/>

Lanczos (here: ~1,3KB):

<img style="width: 50%; display: block; image-rendering: optimizeSpeed; image-rendering: -moz-crisp-edges; image-rendering: -o-crisp-edges; image-rendering: -webkit-optimize-contrast; image-rendering: pixelated; image-rendering: optimize-contrast; -ms-interpolation-mode: nearest-neighbor;" src="examples/tmp-pixel-lanczos.jpg"/>

<br/>

The result with no interpolation looks interesting but might be a bit too much. I am probably going to use lanczos.

