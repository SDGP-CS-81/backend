import { Request, Response, NextFunction } from 'express';
import Logger from '../logger';

export const loggerMiddleware = (req: Request, res: Response, next: NextFunction) => {
    const start = process.hrtime();
    // Log the incoming request details
    Logger.info(`${req.method} ${req.originalUrl} [REQUEST] IP: ${req.ip}, X-Forwarded-For: ${req.headers['x-forwarded-for'] || 'N/A'}`);
  
    res.on('finish', () => {
      const elapsed = process.hrtime(start);
      const elapsedTimeMs = (elapsed[0] * 1000) + (elapsed[1] / 1000000);
      Logger.info(`${req.method} ${req.originalUrl} [RESPONSE] ${res.statusCode} ${elapsedTimeMs.toFixed(3)} ms, IP: ${req.ip}, X-Forwarded-For: ${req.headers['x-forwarded-for'] || 'N/A'}`);
    });
  
    next();
  };
  
