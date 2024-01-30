import opencv from "@u4/opencv4nodejs";
import { getVideoDataStoryboard } from "./VideoDataDownloader";

export const getVideoAnalysis = async (videoID: string) => {
  console.log(videoID);
  const images = await getVideoDataStoryboard(videoID);
  const filteredImages = filterDetailOutliers(images);

  const quality = getVideoDetailScore(
    (await filteredImages).map((image) => image.score),
  );

  return {
    categoryScores: { nature: 0.5, urban: 0.5, lowlight: 0.5 },
    frameScores: { detailScore: quality },
  };
};

export const getVideoDetailScore = (imageScores: number[]) => {
  // get the mean variance from all the frames
  // the mean variance of all frames is considered the mean
  // quality level for the video

  return imageScores.reduce((i, j) => i + j) / imageScores.length;
};

export const filterDetailOutliers = async (images: Buffer[]) => {
  // we have to work with multiple frames for a video
  // in order to avoid outlier frames (title cards etc)
  // from poisoning the data these frames must be discarded.
  // we find the standard deviation for the variance of all frames
  // and then discard any frames that may be outliers

  const imageScores = await getLaplacianVariance(images);

  const { numMean: scoresMean, numStdDev: scoresStdDev } =
    getMeanStdDev(imageScores);

  const devLowerBound = scoresMean - scoresStdDev;
  const devUpperBound = scoresMean + scoresStdDev;

  // filter out any frames that have a variance that is beyond the standard deviation
  const filteredImages = images
    .map((image, index) => {
      return { image, score: imageScores[index] };
    })
    .filter(
      (imageScore) =>
        imageScore.score >= devLowerBound && imageScore.score <= devUpperBound,
    );

  return filteredImages.sort();
};

const getLaplacianVariance = async (images: Buffer[]) => {
  // convolve the images (grayscale) with the laplacian operator.
  // this will return all the edges (rapid intensity changes) in the image
  // the higher the detail of the image the more variance there is
  // between edges and flat planes.

  const imageScores = [];

  for (let index = 0; index < images.length; index++) {
    // the variance of a sequence is the standard deviation squared
    const data = (
      await (
        await (
          await opencv.imdecodeAsync(images[index], opencv.IMREAD_GRAYSCALE)
        ).laplacianAsync(opencv.CV_64F)
      ).meanStdDevAsync()
    ).stddev.getDataAsArray();

    imageScores.push(Math.pow(data[0][0], 2));
  }

  return imageScores;
};

const getMeanStdDev = (numArray: number[]) => {
  const numMean = numArray.reduce((i, j) => i + j) / numArray.length;

  const numStdDev = Math.sqrt(
    numArray
      .map((frame) => Math.pow(frame - numMean, 2))
      .reduce((i, j) => i + j) / numArray.length,
  );

  return { numMean, numStdDev };
};
