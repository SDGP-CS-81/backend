import ytdl from "ytdl-core";
import sharp from "sharp";
import { youtube } from "@googleapis/youtube";

export const getVideoDataStoryboard = async (videoId: string) => {
  const vidUrl = `https://www.youtube.com/watch?v=${videoId}`;
  // the highest resolution storyboard is the last one
  const sb = (await ytdl.getInfo(vidUrl)).videoDetails.storyboards.pop();
  const frames: Buffer[] = [];

  if (sb === undefined) {
    return frames;
  }

  // a single storyboard may be split over multiple image atlases
  for (let sbCount = 0; sbCount < sb.storyboardCount; sbCount++) {
    const response = await fetch(
      sb.templateUrl.replace("$M", sbCount.toString()),
    );
    const imageBuffer = await (await response.blob()).arrayBuffer();
    const sbMetadata = await sharp(imageBuffer).metadata();

    const sbWidth = sb.thumbnailWidth;
    const sbHeight = sb.thumbnailHeight;
    const sbMetaWidth = sbMetadata.width ? sbMetadata.width : 0;
    const sbMetaHeight = sbMetadata.height ? sbMetadata.height : 0;

    // the last atlas in a storyboard may have fewer rows
    // check for that and make sure we don't try to extract content
    // from outside the image bounds
    const sbCols =
      sbMetaWidth < sbWidth * sb.columns
        ? Math.round(sbMetaWidth / sbWidth)
        : sb.columns;
    const sbRows =
      sbMetaHeight < sbHeight * sb.rows
        ? Math.round(sbMetaHeight / sbHeight)
        : sb.rows;

    for (let row = 0; row < sbRows; row++) {
      for (let col = 0; col < sbCols; col++) {
        // extract each of the frames in the atlas
        const collage = sharp(imageBuffer);

        const extractOpts = {
          left: sbWidth * col,
          top: sbHeight * row,
          width: sbWidth,
          height: sbHeight,
        };

        const extractedImage = collage.extract(extractOpts);

        frames.push(await extractedImage.png().toBuffer());
      }
    }
  }

  console.log(`Extracted storyboard for video: ${vidUrl}`);
  return frames;
};

export const getVideoDataText = async (videoId: string) => {
  const ytClient = youtube({
    version: "v3",
    auth: process.env.YT_API_KEY,
  });

  const videoDetails = (
    await ytClient.videos.list({
      part: ["snippet", "status"],
      id: [videoId],
    })
  ).data;

  const videoItem = videoDetails.items?.shift();

  const videoCategory = (
    await ytClient.videoCategories.list({
      part: ["snippet"],
      id: [`${videoItem?.snippet?.categoryId}`],
    })
  ).data;

  const categoryItem = videoCategory.items?.shift();

  return {
    title: videoItem?.snippet?.title,
    description: videoItem?.snippet?.description,
    category: categoryItem?.snippet?.title,
    channelId: videoItem?.snippet?.channelId,
  };
};
