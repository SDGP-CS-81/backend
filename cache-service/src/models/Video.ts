import { Schema, model } from "mongoose";

export type VideoDocument = Document & {
  _id: string;
};

const videoSchema = new Schema<VideoDocument>({
  _id: {
    type: String,
    required: true,
  },
});

export const Video = model<VideoDocument>("Video", videoSchema);
