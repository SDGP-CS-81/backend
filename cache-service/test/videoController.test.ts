import request from "supertest";
import { app } from "../src/app";
import { Video } from "../src/models/Video";
import { describe, it, beforeEach, expect, jest } from "@jest/globals";

jest.mock("../src/models/Video");

const mockedVideoModel = Video as jest.Mocked<typeof Video>;

beforeEach(() => {
  mockedVideoModel.findById.mockClear();
  mockedVideoModel.create.mockClear();
  mockedVideoModel.findByIdAndUpdate.mockClear();
  mockedVideoModel.findByIdAndDelete.mockClear();
});

describe("Video Controller", () => {
  it("GET /api/video/:videoid - should return video if exists", async () => {
    const videoID = "some-existing-video-id";
    mockedVideoModel.findById.mockResolvedValue({ _id: videoID });

    const response = await request(app).get(`/api/video/${videoID}`);
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ _id: videoID });
  });

  it("POST /api/video/:videoid - should create a new video", async () => {
    const videoData = {
      _id: "new-video-id",
      imageScores: {
        graphics: 0.1,
        lowLight: 0.2,
        nature: 0.3,
        person: 0.4,
        sports: 0.5,
        textHeavy: 0.6,
        news: 0.7,
      },
      frameScores: {},
      textScores: {},
    };
    mockedVideoModel.create.mockResolvedValue(videoData as any);

    const response = await request(app)
      .post("/api/video/${videoID}")
      .send(videoData);
    expect(response.status).toBe(200);
    expect(response.body).toEqual(videoData);
  });
});
