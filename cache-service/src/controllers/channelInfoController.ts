import { Request, Response } from 'express';

export const incrementVoteCount = async (req: Request, res: Response) => {
  const { channelId, category } = req.body;
  if (!channelId || !category) {
      return res.status(400).json({ error: 'Missing channelId or category' });
  }
};
