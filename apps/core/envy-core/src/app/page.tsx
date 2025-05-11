"use client";
import Image from "next/image";
import CookieChecker from "@/components/LoginHelperClient";
import { signToken, decodeToken } from "@/components/LoginHelper";
import { useEffect, useState } from "react";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    async function checkAuth() {
      const result = await CookieChecker();
      // @ts-ignore
      setIsAuthenticated(result);
    }
    checkAuth();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 font-[family-name:var(--font-geist-sans)]">
      {isAuthenticated ? (
        // Navbar with dashboard and other links
        <p>Placeholder Content</p>
      ) : (
        // Login prompt
        // TODO: Add login forms
          <div className="card rounded-2xl"><h1 className="text-4xl">Login</h1></div>
      )}
    </main>
  );
}
