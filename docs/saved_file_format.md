# pictonode saved file format

The pictonode saved file format is a ZIP file containing the following:

- The JSON pipeline file, but with the "input" template's "image" value replaced with the name of the image file in the zip.
- The image files in question.

## Node pipeline Node names:

**Image Source Node**: 'ImgSrc'
**Image Output Node**: 'ImgOut'
**Image Invert Node**: 'Invert'
**Gaussian Blur Node**: 'GaussBlur'
**Composite Node**: 'CompOver'
**Brightness Contrast Node**: 'BrightCont'