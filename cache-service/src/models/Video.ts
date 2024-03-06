import { Schema, model } from "mongoose";

export type ImageScores = Document & {
  graphics: number;
  lowLight: number;
  nature: number;
  person: number;
  sports: number;
  textHeavy: number;
  news: number;
};

const imageScores = new Schema<ImageScores>(
  {
    graphics: Number,
    lowLight: Number,
    nature: Number,
    person: Number,
    sports: Number,
    textHeavy: Number,
    news: Number,
  },
  { _id: false }
);

export type FrameScores = Document & { [key: string]: number };

const frameScores = new Schema<FrameScores>({}, { _id: false });

export type TextScores = Document & { [key: string]: number };

const textScores = new Schema<TextScores>({}, { _id: false });

export type VideoDocument = Document & {
  _id: string;
  imageScores: ImageScores;
  frameScores: FrameScores;
  textScores: TextScores;
};

const videoSchema = new Schema<VideoDocument>({
  _id: {
    type: String,
    required: true,
  },
  imageScores: {
    type: imageScores,
    required: false,
  },
  // choose better name for this perhaps
  frameScores: {
    type: frameScores,
    required: false,
  },
  textScores: {
    type: textScores,
    required: false,
  },
});

export const Video = model<VideoDocument>("Video", videoSchema);
