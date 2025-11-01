export const metadata = {
  title: "Resume Annotation Assistant",
  description: "Non-destructive resume suggestions aligned to a JD"
};

import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif" }}>{children}</body>
    </html>
  );
}

