import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import MainLayout from "@/components/MainLayout";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Soutien Pédagogique | Universités Marocaines",
  description: "Système de Recommandation Intelligente de Soutien Pédagogique",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className={inter.variable} data-scroll-behavior="smooth">
      <body className={`${inter.className} antialiased bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-100 min-h-screen`}>
        <MainLayout>
          {children}
        </MainLayout>
      </body>
    </html>
  );
}
