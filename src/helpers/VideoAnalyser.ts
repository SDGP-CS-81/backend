import opencv from "@u4/opencv4nodejs";

export const getVideoDetailScore = async (images: Buffer[]) => {
  // convolve the images (grayscale) with the laplacian operator.
  // this will return all the edges (rapid intensity changes) in the image
  // the higher the detail of the image the more variance there is
  // between edges and flat planes.
  const frames = images.map((image) =>
    Math.pow(
      // the variance of a sequence is the standard deviation squared
      opencv
        .imdecode(image, opencv.IMREAD_GRAYSCALE)
        .laplacian(opencv.CV_64F)
        .meanStdDev()
        .stddev.getDataAsArray()[0][0],
      2,
    ),
  );

  // we have to work with multiple frames for a video
  // in order to avoid outlier frames (title cards etc)
  // from poisoning the data these frames must be discarded.
  // we find the standard deviation for the variance of all frames
  // and then discard any frames that may be outliers

  // calculate the mean of the variance for all frames
  const framesMean = frames.reduce((i, j) => i + j) / frames.length;
  // calculate the stddev among the variance of all the frames
  const framesStdDev = Math.sqrt(
    frames
      .map((frame) => Math.pow(frame - framesMean, 2))
      .reduce((i, j) => i + j) / frames.length,
  );

  const devLowerBound = framesMean - framesStdDev;
  const devUpperBound = framesMean + framesStdDev;

  // filter out any frames that have a variance that is beyond the standard deviation
  const filteredFrames = frames.filter(
    (frame) => frame <= devUpperBound && frame >= devLowerBound,
  );

  // get the mean variance from all the frames
  // the mean variance of all frames is considered the mean
  // quality level for the video
  return filteredFrames.reduce((i, j) => i + j) / filteredFrames.length;
};

// dummy function to simulate the video analyser class
// come up with better names if u can for these properties
export const videoAnalyserClass = (videoID: string) => {
  console.log(videoID);
  return {
    categoryScores: { nature: 0.5, urban: 0.5, lowlight: 0.5 },
    frameScores: { someField: "someValue" },
  };
};
