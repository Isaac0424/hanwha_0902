import type { Metadata } from "next";
import "./globals.css";
import "./generation.css";
import "./studio.css";
import {Workspace} from "@/components/workspace";

export const metadata: Metadata = {
  title: "RAG Explorer | 눈으로 이해하는 RAG 시스템",
  description: "청킹, 임베딩, 검색, 재정렬, 컨텍스트 구성과 평가까지 직접 조작하며 배우는 인터랙티브 RAG 학습 사이트",
  icons: {
    icon: "/favicon-cat.png",
    shortcut: "/favicon-cat.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="antialiased"><Workspace>{children}</Workspace></body>
    </html>
  );
}
