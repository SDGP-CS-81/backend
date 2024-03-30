import { Request, Response } from "express";
import {
  CategoriesDocument,
  ChannelDocument,
  Channel,
} from "../models/Channel";
import Logger from "../logger";

export const getHighestVoteForChannel = async (req: Request, res: Response) => {
  try {
    const channelId: string = req.params.channelId;
    Logger.info(
      `Received request to get highest vote for channel ${channelId}`
    );

    // find channel using channel id
    const channel: ChannelDocument | null = await Channel.findById(channelId);

    let mostVotedCategory: string | null = null;

    // if channel not found, return null
    if (!channel) {
      Logger.warn(`Channel ${channelId} not found`);
      return res.json({ mostVotedCategory });
    }

    // check if categories for channel is not null before accessing
    if (!channel.categories) {
      Logger.error(`Categories not found for the channel ${channelId}`);
      return res
        .status(500)
        .json({ message: "Categories not found for the channel" });
    }

    const { categories } = channel;

    // check if all category votes are zero
    const allZeroVotes: boolean = Object.values(categories).every(
      (votes) => votes === 0
    );

    // if all category votes are zero, return null
    if (allZeroVotes) {
      Logger.info(`All category votes are zero for channel ${channelId}`);
      return res.json({ mostVotedCategory: null });
    }

    // find the most voted category
    let maxVotes: number = 0;
    // flag to track if there are multiple categories with the same votes
    let multipleCategoriesWithSameVotes: boolean = false;
    for (const [category, votes] of Object.entries(categories)) {
      if (votes > maxVotes) {
        mostVotedCategory = category;
        maxVotes = votes;
        // reset the flag if there is a category with more votes
        multipleCategoriesWithSameVotes = false;
      } else if (votes === maxVotes) {
        // set the flag if there is a category with the same votes as the current maxVotes
        multipleCategoriesWithSameVotes = true;
      }
    }

    // if there are multiple categories with the same non-zero votes, set most voted category to null
    if (multipleCategoriesWithSameVotes && maxVotes !== 0) {
      Logger.info(
        `Multiple categories with the same non-zero votes for channel ${channelId}`
      );
      mostVotedCategory = null;
    }

    // Return the most voted category
    res.json({ mostVotedCategory });
  } catch (error) {
    Logger.error(
      `Internal server error while getting highest vote for channel: ${
        error instanceof Error ? error.message : ""
      }`
    );
    res.status(500).json({ message: "Internal server error" });
  }
};

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
    Logger.info(
      `Received request to increment vote count for channel ${channelId} and category ${category}`
    );
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

    // save the updated channel document
    await channel.save();

    Logger.info(
      `Vote count incremented successfully for channel ${channelId} and category ${category}`
    );
    return res
      .status(200)
      .json({ message: "Vote count incremented successfully" });
  } catch (error) {
    Logger.error(
      `Internal server error: ${error instanceof Error ? error.message : ""}`
    );
    return res.status(500).json({ error: "Internal server error" });
  }
};
