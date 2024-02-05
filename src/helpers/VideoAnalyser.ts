import opencv from "@u4/opencv4nodejs";
import {
  getVideoDataStoryboard,
  getVideoDataText,
} from "./VideoDataDownloader";
import ModelWrapper from "./ModelWrapper";

export const getVideoAnalysis = async (
  videoID: string,
  categoryKeywords: any,
) => {
  console.log(videoID);
  const images = await getVideoDataStoryboard(videoID);
  const filteredImages = await filterDetailOutliers(images);
  const modelWrapper = await ModelWrapper.getInstance();
  const categoryScores = modelWrapper.predict(
    ModelWrapper.preprocess(filteredImages[0].image),
  );

  const quality = getVideoDetailScore(
    filteredImages.map((image) => image.score),
  );

  const videoText = await getVideoDataText(videoID);
  const keywordScores = getVideoKeywordScore(videoText, categoryKeywords);

  return {
    categoryScores,
    frameScores: { detailScore: quality },
    keywordScores,
  };
};

export const getVideoKeywordScore = (
  videoText: {
    title: string;
    description: string;
    category: string;
    channelId: string;
  },
  categoryKeywords: any,
) => {
  const catKeywordEntries = Object.entries(categoryKeywords);

  return Object.fromEntries(
    catKeywordEntries.map((entry) => {
      let count = 0;

      (entry[1] as string[]).forEach((keyword) => {
        Object.values(videoText).forEach((text) => {
          const matches = text
            .toLowerCase()
            .match(`\\W${keyword.toLowerCase()}\\W`); // this is where matching happens
          // this regex simply ensures that the keyword is surrounded by non-word chars

          // simply increment a single counter
          // this could possibly be extended to individual counts
          // for each text section like title, description etc.
          count += matches ? matches.length : 0;
        });
      });

      entry[1] = count;
      return entry;
    }),
  );
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
