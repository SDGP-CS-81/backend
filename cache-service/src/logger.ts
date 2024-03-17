import winston from 'winston';
import path from 'path';

const LOG_DIR = path.join(__dirname, '../../debug.log');

const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
};

const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white',
};

winston.addColors(colors);

const format = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.colorize({ all: true }),
  winston.format.printf((info) => `${String(info.timestamp)} ${info.level} ${String(info.message)}`),
);

const transports = [
  new winston.transports.Console(),
  new winston.transports.File({
    filename: LOG_DIR,
    level: 'debug',
  }),
];

const Logger = winston.createLogger({
  level: process.env.NODE_ENV === 'development' ? 'debug' : 'warn',
  levels,
  format,
  transports,
});

export default Logger;
