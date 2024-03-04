import request from "supertest";
import { describe, it, beforeEach,expect,jest } from "@jest/globals";
import { app } from "../src/app";
import { VideoModel } from "../src/models/Video";


jest.mock("../src/models/Video", () => {
  return {
    findById: jest.fn(),
    create: jest.fn(),
    updateOne: jest.fn(),
    findByIdAndDelete: jest.fn(),
  };
});

  const videoModel = jest.mocked(VideoModel)

beforeEach(() => {
  // Clear all instances and calls to constructor and all methods:
  (VideoModel.findById as jest.Mock).mockClear();
  (VideoModel.create as jest.Mock).mockClear();
  (VideoModel.updateOne as jest.Mock).mockClear();
  (VideoModel.findByIdAndDelete as jest.Mock).mockClear();
});

describe("Video Controller", () => {
  it("GET /api/video/:videoid - should return video if exists", async () => {
    const videoID = 'some-existing-video-id';
    // Mock the findById method to return a video
      (videoModel.findById).mockResolvedValue({ _id: videoID});

    const response = await request(app).get(`/api/video/${videoID}`);
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ _id: videoID });
  });

  it("POST /api/video - should create a new video", async () => {
    // const videoData = {
    //   _id: 'new-video-id',
    //   categoryScores: {
    //     lowGraphics: 0.1,
    //     lowLight: 0.2,
    //     nature: 0.3,
    //     person: 0.4,
    //     sports: 0.5,
    //     textHeavy: 0.6,
    //     news: 0.7,
    //   },
    //   frameScores: {},
    //   keywordScores: {},
    // };
    // Mock the create method to return the new video



    const videoData = {
      _id: 'new-video-id',
      categoryScores: {
        lowGraphics: 0.1,
        lowLight: 0.2,
        nature: 0.3,
        person: 0.4,
        sports: 0.5,
        textHeavy: 0.6,
        news: 0.7,
      },
      frameScores: {},
      keywordScores: {},
    };
    

    videoModel.create.mockResolvedValue(videoData as any);

    const response = await request(app).post("/api/video").send(videoData);
    expect(response.status).toBe(200);
    expect(response.body).toEqual(videoData);
  });

  it("PUT /api/video/:videoid - should update an existing video", async () => {
    const videoID = 'some-existing-video-id';
    const updatedData = {
      categoryScores: {
        lowGraphics: 0.2,
        lowLight: 0.3,
        nature: 0.4,
        person: 0.5,
        sports: 0.6,
        textHeavy: 0.7,
        news: 0.8,
      },
    };
    // Mock the findById method to return the existing video
    videoModel.findById.mockResolvedValue({ _id: videoID });
    // Mock the updateOne method to return that it updated one video
    
    // (videoModel.updateOne).mockResolvedValue({ person: 1 });

    const response = await request(app).put(`/api/video/${videoID}`).send(updatedData);
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ nModified: 1 });
  });

  it("DELETE /api/video/:videoid - should delete an existing video", async () => {
    const videoID = 'some-existing-video-id';
    // Mock the findByIdAndDelete method to return the deleted video
    (videoModel.findByIdAndDelete ).mockResolvedValue({ _id: videoID });

    const response = await request(app).delete(`/api/video/${videoID}`);
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ _id: videoID });
  });
});


