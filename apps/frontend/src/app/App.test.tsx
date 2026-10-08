import {renderToStaticMarkup} from "react-dom/server";
import {describe, expect, it} from "vitest";
import {App} from "./App";

describe("App", () => {
  it("renders a complete studio workspace shell", () => {
    const html = renderToStaticMarkup(<App />);

    expect(html).toContain('aria-label="Primary"');
    expect(html).toContain("Preference Lab");
    expect(html).toContain("Design Preview");
    expect(html).toContain("Material Harmony");
  });
});
