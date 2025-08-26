import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ERI Potter",
  description: "MSA Project",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // 레이아웃 로딩 로그
  console.log("🔧 RootLayout 렌더링 시작");
  
  try {
    return (
      <html lang="ko">
        <body className={inter.className}>{children}</body>
      </html>
    );
  } catch (error) {
    console.error("❌ RootLayout 렌더링 실패", error as Error);
    throw error;
  }
}
