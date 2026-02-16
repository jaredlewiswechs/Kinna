import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Nav } from "@/components/nav";

export const metadata: Metadata = {
  title: "Kinna — Kinematic Linguistics",
  description:
    "A geometric substrate for semantic reliability. Explore language as geometry.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#FFFFFF",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <div className="flex flex-col lg:flex-row min-h-screen">
          <Nav />
          <main className="flex-1 lg:ml-[260px] pb-24 lg:pb-0">
            <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
