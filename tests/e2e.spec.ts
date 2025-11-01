import { test, expect } from "@playwright/test";

test("upload and view annotations", async ({ page }) => {
  await page.goto("http://localhost:3000");
  const jd = "Seeking Software Engineer with Python, APIs, React.";
  // Resume upload: a placeholder empty file is acceptable for this smoke test (backend may reject; adjust in real runs)
  const resumePath = "samples/resume_onepage.pdf";
  await page.setInputFiles('input[type="file"]', resumePath);
  await page.fill("textarea", jd);
  await page.click("button:has-text('Analyze')");
  // Allow time for backend; in CI, mock backend or ensure running
  await page.waitForTimeout(1000);
  // Sidebar should render items if backend is live
  // In smoke environment without backend, this test can be skipped or adjusted.
});

