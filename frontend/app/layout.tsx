import type { Metadata, Viewport } from "next";
import { Inter, Poppins } from "next/font/google";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { AuthProvider } from "@/components/providers/auth-provider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap", // Prevents FOIT (Flash of Invisible Text)
  preload: true,
  variable: "--font-inter",
});

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["700"], // Only bold for brand name
  display: "swap",
  preload: true,
  variable: "--font-brand",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f8f8fc" },
    { media: "(prefers-color-scheme: dark)", color: "#0f0f1a" },
  ],
};

export const metadata: Metadata = {
  title: "TaskFlow - Modern Task Management",
  description: "A modern, responsive task management application",
  keywords: ["task management", "todo", "productivity"],
  robots: "index, follow",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${poppins.variable} font-sans antialiased`}>
        <ThemeProvider>
          <AuthProvider>
            {children}
            <Toaster position="bottom-right" richColors closeButton />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
