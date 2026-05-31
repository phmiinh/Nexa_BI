import type { Metadata } from "next";
import { AppNav } from "@/components/AppNav";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";
import "./globals.css";

export const metadata: Metadata = {
  title: "SocialLens BI",
  description: "Business intelligence dashboard for social media performance"
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = await getRequestLocale();
  const dictionary = getDictionary(locale);

  return (
    <html lang={locale}>
      <body>
        <div className="app-shell">
          <AppNav labels={dictionary.nav} languageLabels={dictionary.language} locale={locale} />
          {children}
        </div>
      </body>
    </html>
  );
}
