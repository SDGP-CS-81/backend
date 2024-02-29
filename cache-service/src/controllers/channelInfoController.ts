import { Request, Response } from 'express';
import Channel from '../models/ChannelInfo';

export const incrementVoteCount = async (req: Request, res: Response) => {
  const { channelId, category } = req.body;
  if (!channelId || !category) {
      return res.status(400).json({ error: 'Missing channelId or category' });
  }

  try {
      let channel = await Channel.findOne({ channelId });

      if (!channel) {
          channel = new Channel({ channelId, categories: {} });
      }

      // initialize category count if not present
      if (channel.categories && channel.categories[category] === undefined) {
          channel.categories[category] = 0;
      }

      // increment the vote count for the specified category
      channel.categories[category]++;

      console.log(`Vote count for category ${category} in channel ${channelId}: ${channel.categories[category]}`);

      // save the updated channel document
      await channel.save();
      
      return res.status(200).json({ message: 'Vote count incremented successfully' });
  } catch (error) {
      console.error('Error incrementing vote count:', error);
      return res.status(500).json({ error: 'Internal server error' });
  }
};
