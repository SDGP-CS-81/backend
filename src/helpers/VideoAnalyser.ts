import opencv from "@u4/opencv4nodejs";
import {
  getVideoDataStoryboard,
  getVideoDataText,
} from "./VideoDataDownloader";
import ModelWrapper from "./ModelWrapper";
import fs from "fs/promises";

export const getVideoAnalysis = async (
  videoID: string,
  categoryKeywords: { [key: string]: string[] },
) => {
  console.log(videoID);
  const images = await getVideoDataStoryboard(videoID);
  const filteredImages = (await filterDetailOutliers(images)).sort(
    (first, second) => {
      return first.score - second.score;
    },
  );

  // use the highest detail image as a pivot to diff all the other images
  const highestDetailImage = filteredImages[filteredImages.length - 1];

  // calculate the difference of the edges with the pivot image
  const diffOfImages = filteredImages.map((first) => {
    const diff = highestDetailImage.laplaceMap.absdiff(first.laplaceMap).sum();

    return typeof diff === "number" ? diff : 0;
  });

  const { numMean, numStdDev } = getMeanStdDev(diffOfImages);
  const devUpperBound = numMean + numStdDev;
  const devLowerBound = numMean - numStdDev;

  // remove all the images that fall out of the std deviation
  // further helps us get rid of outlier content
  // as an example this reliably removes the talking person segments
  // in coding videos
  const diffedFilteredImages = diffOfImages
    .map((image, index) => {
      return {
        ...filteredImages[index],
        diff: image,
      };
    })
    .filter((item) => {
      return item.diff >= devLowerBound && item.diff <= devUpperBound;
    })
    .sort((first, second) => {
      // sort based on the difference distance
      return first.diff - second.diff;
    });

  const predictionImage =
    diffedFilteredImages[Math.round(diffedFilteredImages.length / 2)]; // use the mid distance/diff image

  if (process.env.NODE_ENV !== "production") {
    diffedFilteredImages.forEach((image) =>
      console.log(image.score, image.diff),
    );

    diffedFilteredImages.forEach(async (item, index) => {
      await opencv.imwriteAsync(`${index}.png`, item.laplaceMap);
    });

    await fs.writeFile("predicted_image.png", predictionImage.image);
  }

  const modelWrapper = await ModelWrapper.getInstance();
  const categoryScores = modelWrapper.predict(
    ModelWrapper.preprocess(predictionImage.image),
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
  categoryKeywords: { [key: string]: string[] },
) => {
  const keywordScores: { [key: string]: number } = {};
  const textToSearch = Object.values(videoText).join(" ");

  Object.entries(categoryKeywords).forEach(([category, keywords]) => {
    const matchedScores = keywords.map(
      (keyword) =>
        (textToSearch.match(new RegExp(`\\W${keyword}\\W`, "g")) || []).length,
    );

    const numKeywordsMatched = matchedScores.filter(
      (matchCount) => matchCount > 0,
    ).length;

    keywordScores[category] = numKeywordsMatched;
  });

  return keywordScores;
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

  const { imageScores, laplaceMaps } = await getLaplacianMapVariance(images);

  const { numMean: scoresMean, numStdDev: scoresStdDev } =
    getMeanStdDev(imageScores);

  const devLowerBound = scoresMean - scoresStdDev;
  const devUpperBound = scoresMean + scoresStdDev;

  // filter out any frames that have a variance that is beyond the standard deviation
  const filteredImages = images
    .map((image, index) => {
      return {
        image,
        laplaceMap: laplaceMaps[index],
        score: imageScores[index],
      };
    })
    .filter(
      (imageScore) =>
        imageScore.score >= devLowerBound && imageScore.score <= devUpperBound,
    );

  return filteredImages;
};

const getLaplacianMapVariance = async (images: Buffer[]) => {
  // convolve the images (grayscale) with the laplacian operator.
  // this will return all the edges (rapid intensity changes) in the image
  // the higher the detail of the image the more variance there is
  // between edges and flat planes.

  const imageScores = [];
  const laplaceMaps = [];

  for (let index = 0; index < images.length; index++) {
    // the variance of a sequence is the standard deviation squared
    const laplaceMap = await (
      await opencv.imdecodeAsync(images[index], opencv.IMREAD_GRAYSCALE)
    ).laplacianAsync(opencv.CV_64F);

    const imageScore = (
      await laplaceMap.meanStdDevAsync()
    ).stddev.getDataAsArray();

    imageScores.push(Math.pow(imageScore[0][0], 2));
    laplaceMaps.push(laplaceMap);
  }

  return { imageScores: imageScores, laplaceMaps: laplaceMaps };
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
