import { Schema, model } from "mongoose";

export type CategoryScores = Document & {
  lowGraphics: number;
  lowLight: number;
  nature: number;
  person: number;
  sports: number;
  textHeavy: number;
  news: number;
};

const categoryScores = new Schema<CategoryScores>(
  {
    lowGraphics: Number,
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

export type KeywordScores = Document & { [key: string]: number };

const keywordScores = new Schema<KeywordScores>({}, { _id: false });

export type VideoDocument = Document & {
  _id: string;
  categoryScores: CategoryScores;
  frameScores: FrameScores;
  keywordScores: KeywordScores;
};

const videoSchema = new Schema<VideoDocument>({
  _id: {
    type: String,
    required: true,
  },
  categoryScores: {
    type: categoryScores,
    required: false,
  },
  // choose better name for this perhaps
  frameScores: {
    type: frameScores,
    required: false,
  },
  keywordScores: {
    type: keywordScores,
    required: false,
  },
});

export const Video = model<VideoDocument>("Video", videoSchema);
