import console from "node:console";
import process from "node:process";
import { createVitest } from "vitest/node";

// Used only after the normal failing gate. Read original fields before CLI
// stack formatting; never replace or waive the normal test result.
let context;
try {
  context = await createVitest({ run: true, watch: false, reporters: [] });
  const specifications = await context.globTestSpecifications();
  console.error(
    "Discovered test modules:",
    specifications.map((s) => s.moduleId),
  );
  await context.start();
} catch (error) {
  console.error(
    "Native startup diagnostic:",
    JSON.stringify({
      name: error?.name,
      message: error?.message,
      causeName: error?.cause?.name,
      causeMessage: error?.cause?.message,
      code: error?.code,
    }),
  );
  process.exitCode = 1;
} finally {
  await context?.close();
}
