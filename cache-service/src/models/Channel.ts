import { Document, Schema, model } from "mongoose";

export type CategoriesDocument = Document & {
  music: number;
  podcast: number;
  gaming: number;
  news: number;
  coding: number;
  sports: number;
  graphics: number;
  lifestyle: number;
  nature: number;
  demo: number;
};
export type ChannelDocument = Document & {
  _id: string;
  categories: CategoriesDocument;
};

const channelSchema = new Schema<ChannelDocument>({
  _id: {
    type: String,
    required: true,
  },
  categories: {
    music: { type: Number, default: 0 },
    podcast: { type: Number, default: 0 },
    gaming: { type: Number, default: 0 },
    news: { type: Number, default: 0 },
    coding: { type: Number, default: 0 },
    sports: { type: Number, default: 0 },
    graphics: { type: Number, default: 0 },
    lifestyle: { type: Number, default: 0 },
    nature: { type: Number, default: 0 },
    demo: { type: Number, default: 0 },
  },
});

export const Channel = model<ChannelDocument>("channel", channelSchema);
