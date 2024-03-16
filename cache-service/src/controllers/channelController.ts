import { Request, Response } from "express";
import { CategoriesDocument, ChannelDocument, Channel } from "../models/Channel";


export const getHighestVoteForChannel = async (req: Request, res: Response) => {
  try {
    const channelId: string = req.params.channelId;
    console.log(channelId)

    // find channel using channel id
    const channel: ChannelDocument | null = await Channel.findById(channelId);

    let mostVotedCategory: string | null = null;

    // if channel not found, return null
    if (!channel) {
      return res.json({ mostVotedCategory });
    }

    console.log('Categories and votes for channel:', channel._id);
    console.log(channel.categories);

    // check if categories for channel is not null before accessing
    if (!channel.categories) {
      return res.status(500).json({ message: 'Categories not found for the channel' });
    }

    const { categories } = channel;
    
    // find the most voted category
    let maxVotes: number = 0;
    for (const [category, votes] of Object.entries(categories)) {
      if (votes > maxVotes) {
        mostVotedCategory = category;
        maxVotes = votes;
    }
  }

    // Return the most voted category
    res.json({ mostVotedCategory });

  } catch (error) {
    console.error('Error while fetching channel:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}

type IncrementVoteCountBody = {
  channelId: string;
  category: keyof CategoriesDocument;
};


export const incrementVoteCount = async (req: Request, res: Response) => {
  const { channelId, category }: IncrementVoteCountBody = req.body;
  if (!channelId || !category) {
    return res.status(400).json({ error: "Missing channelId or category" });
  }

  try {
    let channel = await Channel.findById(channelId);

    if (!channel) {
      channel = new Channel({ _id: channelId });
    }

    // if the category doesn't exist in the channel, return an error
    if (channel.categories && channel.categories[category] === undefined) {
      return res.status(409).json({ message: "Invalid category" });
    }

    // increment the vote count for the specified category
    channel.categories[category]++;

    console.log(
      `Vote count for category ${category} in channel ${channelId}: ${channel.categories[category]}`
    );

    // save the updated channel document
    await channel.save();

    return res
      .status(200)
      .json({ message: "Vote count incremented successfully" });
  } catch (error) {
    console.error("Error incrementing vote count:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
};
