# ByteSense - Backend

## Usage & Development

Please read this [article](https://cbea.ms/git-commit/) to learn how to write good commit messages.

### Dependencies

- `nodejs` >= 18.0
- `python3` <= 3.11 (Only needed for converting the keras model to a tfjs compatible one)
- `npm` >= 10.0
- `tensorflow` >= 2.0
- `tensorflowjs` >= 4.0
- `libopencv` >= 4.0 (This could be built from source however the project is only tested with the prebuilt packages from Debian 12 and Fedora 39)

#### API Keys

- The YT_API_KEY environment variable needs to be set with a valid key obtained from [Google](https://console.cloud.google.com/) with access to the [YouTube Data API](https://developers.google.com/youtube/v3/getting-started) enabled.
- The MONGODB_URI environment variable also needs to be set to point to a database with full read and write permissions.

#### Classification Model

You will also need a trained keras format `model.h5` from the [ML-Model](https://github.com/SDGP-CS-81/ML-Model) repo.

### Building and Running

#### Model Conversion

You need to ensure that you have access to a keras `model.h5` file in the current directory. This model has to be converted into a tfjs graph model before attempting to build and run the project.

We recommend converting the model using a [Conda](https://docs.conda.io/en/latest/) environment.

First clone the Backend repo,

```sh
git clone git@github.com:SDGP-CS-81/Backend.git
mv model.h5 ./Backend
cd Backend
```

Then you can create a conda environment and convert the model.

```sh
conda create -n tf-env python=3.11 tensorflowjs
conda activate tf-env
tensorflowjs_converter --input_format=keras --output_format=tfjs_graph_model model.h5 model
rm model.h5
```

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