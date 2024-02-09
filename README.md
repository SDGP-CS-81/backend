# ByteSense - Backend

## Usage & Development

### Dependencies

- `nodejs` >= 18.0
- `npm` >= 10.0
- `tensorflowjs` >= 4.0
- `libopencv` >= 4.0 (This could be built from source however the project is only tested with the prebuilt packages from Debian 12 and Fedora 39)

#### API Keys

- The YT_API_KEY environment variable needs to be set with a valid key obtained from [Google](https://console.cloud.google.com/) with access to the [YouTube Data API](https://developers.google.com/youtube/v3/getting-started) enabled.
- The MONGODB_URI environment variable also needs to be set to point to a database with full read and write permissions.

### Building and Running

#### Docker

We recommend that you make use of the Dockerfile provided with the project to run the backend. Simply build the image in the standard manner.

In the project directory run,

```sh
docker build -t bytesense .
```

This may take some time as the image needs to download `libopencv` and then link the `nodejs` opencv library to it.

Once the image has been built you may run it. Do make sure to set the environment variables described in the `Dependencies` section.

The project listens on port 5000.

```sh
docker run -d -e MONGODB_URI=$URI -e YT_API_KEY=$KEY -p 5000:5000 bytesense:latest
```


#### NPM Commands

- Build the project -> `npm run build`
- Run the project -> `npm run start`
- Run with hot reloading -> `npm run dev`
