// dummy function to simulate the video analyser class
// come up with better names if u can for these properties
export const videoAnalyserClass = (videoID: string) => {
  console.log(videoID);
  return {
    categoryScores: { nature: 0.5, urban: 0.5, lowlight: 0.5 },
    frameScores: { someField: "someValue" },
  };
};
