import mongoose, { Schema, Document } from 'mongoose';

interface ChannelDocument extends Document {
    channelId: string;
    categories: { [category: string]: number };
}

const categories = {
    music: 0,
    podcast: 0,
    gaming: 0,
    news: 0,
    coding: 0,
    sports: 0,
    graphics: 0,
    lifestyle: 0,
    nature: 0,
    demo: 0
};

const ChannelSchema: Schema = new Schema({
    channelId: {
      type: String,
      required: true 
    },
    categories: {
      type: Schema.Types.Mixed,
      default: categories
    }
});

export default mongoose.model<ChannelDocument>('Channel', ChannelSchema);
