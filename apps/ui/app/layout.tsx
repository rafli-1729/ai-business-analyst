import "./globals.css";

export const metadata = {
  title: "AI Analytics Workspace",
  description: "Natural-language analytics workspace for the Olist warehouse",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
