// Log original error fields without asking Vite to format source-mapped stacks.
// The default reporter remains enabled and still determines the failing exit.
import console from "node:console";

export default class DiagnosticReporter {
  onTestRunEnd(modules, errors) {
    for (const error of errors) {
      console.error(
        "Original test error:",
        JSON.stringify({
          collectedModules: modules.length,
          name: error.name,
          message: error.message,
        }),
      );
    }
  }
}
