import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import React from "react";
import CookieChecker from "@/components/LoginHelperClient";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Envybase Frontend",
  description: "Envybase is a self-hostable, open-source alternative to Firebase.",
    icons: {
        icon: "/favicon.ico",
        shortcut: "/favicon.ico",
        apple: "/apple-touch-icon.png",
    },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white`}
      >
      <nav className="navbar-buttons p-4 navbar rounded-2xl dark:text-white list-none"><li> <a href="/dashboard">Dashboard</a></li><li>Services</li> <div className="float-start"></div> </nav>
        {children}
      </body>
    </html>
  );
}
