import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "MedLit | Medical records, explained at your reading level",
  description:
    "Grounded plain-language explanations of medical records with citations you can check. FHIR + MedlinePlus + openFDA + RxNav.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} ${spaceGrotesk.variable} min-h-screen bg-brand-surface text-gray-900`}
      >
        {children}
      </body>
    </html>
  );
}
