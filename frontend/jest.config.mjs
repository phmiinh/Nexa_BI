import nextJest from "next/jest.js";

const createJestConfig = nextJest({
  dir: "./"
});

const customJestConfig = {
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  testEnvironment: "jest-environment-jsdom",
  testPathIgnorePatterns: ["<rootDir>/.next/", "<rootDir>/node_modules/"],
  collectCoverage: true,
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/app/**/{layout,page,loading,error}.tsx"
  ],
  coverageThreshold: {
    global: {
      branches: 25,
      functions: 35,
      lines: 35,
      statements: 35
    }
  }
};

export default createJestConfig(customJestConfig);
