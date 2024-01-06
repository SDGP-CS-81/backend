import { Schema, model } from "mongoose";

const categoryProbabailities = new Schema({
  nature: Number,
  urban: Number,
  lowlight: Number,
});

const vidInfoSchema = new Schema({
  _id: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  categoryScores: {
    type: categoryProbabailities,
    required: false,
  },
  // choose better name for this perhaps
  frameScores: {
    type: Object,
    required: false,
  },
  userRated: {
    type: String,
    required: false,
  },
});

export const VidInfoModel = model("vidinfo", vidInfoSchema);
