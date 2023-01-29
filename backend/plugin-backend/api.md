# `plugin-backend` API Description

`plugin-backend` uses an HTTP API to communicate with the frontend. The API is defined as follows:

## `POST /api/upload_image`

The body of the `POST` request is expected to be an image file, and `content-type` should accurately reflect the type of the file. If the he response takes the following form:

```json
{
  "variant": 0,
  "id": 12345
}
```

or

```json
{
  "variant": 1,
}
```

The `variant` field indicates whether the image was successfully uploaded. If `variant` is 0, then the image was successfully uploaded and the `id` field contains the ID of the image. If `variant` is 1, then the image was not successfully uploaded.

## `POST /api/process_image`

The body of the `POST` request should be a [serialized pipeline]. The response will be the resulting image file.

[serialized pipeline]: ../../libraries/libnode/README.md#serialization-format
