import type { Config } from "jest";

const config: Config = {
  testEnvironment: "node",

  preset: "ts-jest",

  moduleFileExtensions: ["js", "ts"],
};

export default config;
