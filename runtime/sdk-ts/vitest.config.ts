import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["../tests/sdk-ts/**/*.test.ts"],
  },
  resolve: {
    extensions: [".ts", ".js"],
  },
});
