# pictodeamon

`pictodaemon` is the subprocess responsible for any actual heavy lifting within `pictonode`. It is responsible for:

* Storing and caching images.
* Receiving, parsing and processing node pipelines.
* Managing basic user and ownership information.

It is not responsible for:

* User login, sessions and authentication.
* Hosting the static frontend.
* Exposing an interface through which it can be accessed non-programmatically.
* Saving node pipelines.

For the web, `pictodaemon` is the center of the web backend, which adds these functionalities over an HTTP interface. For the GIMP plugin, `pictodaemon` is wrapped by a simpler script that communicates with the GIMP plugin itself.

## Interface

Two operations are available:

- "upload image": Given image data, save it to the disk and return a global unique ID for the image. The image should be saved to the disk, in a place where it will be accessible for the near future.
- "process pipeline": Given a pipeline (in serialized form), process it and return image data for the final image.
