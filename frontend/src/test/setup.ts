import * as matchers from "@testing-library/jest-dom/matchers";
import type { TestingLibraryMatchers } from "@testing-library/jest-dom/matchers";
import { cleanup } from "@testing-library/react";
import { afterEach, expect, vi } from "vitest";

// Vitest 5 has separate return/value generic parameters. Register the standard
// matchers directly until jest-dom's bundled Vitest augmentation supports them.
declare module "vitest" {
  interface Assertion<R extends void | Promise<void> = void, T = unknown> {
    toBeVisible: TestingLibraryMatchers<T, R>["toBeVisible"];
    toBeInTheDocument: TestingLibraryMatchers<T, R>["toBeInTheDocument"];
    toBeDisabled: TestingLibraryMatchers<T, R>["toBeDisabled"];
    toHaveTextContent: TestingLibraryMatchers<T, R>["toHaveTextContent"];
  }
}
expect.extend(matchers);
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
