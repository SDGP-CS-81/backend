import request from "supertest";
import { describe, it } from "@jest/globals";
import { app } from "../src/app";

describe("Check /api", () => {
  it("should return 404", (done) => {
    request(app).get("/api").expect(404, done);
  });
});
