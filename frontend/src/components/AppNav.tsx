import Link from "next/link";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { NavLinks } from "@/components/NavLinks";
import type { Locale } from "@/lib/i18n";

const items = [
  { href: "/dashboard", key: "dashboard" },
  { href: "/content", key: "content" },
  { href: "/sentiment", key: "sentiment" },
  { href: "/competitors", key: "competitors" },
  { href: "/posts", key: "posts" },
  { href: "/data-health", key: "dataHealth" }
] as const;

type AppNavProps = {
  locale: Locale;
  labels: Record<(typeof items)[number]["key"] | "ariaLabel", string>;
  languageLabels: {
    label: string;
    english: string;
    vietnamese: string;
  };
};

export function AppNav({ locale, labels, languageLabels }: AppNavProps) {
  return (
    <nav className="app-nav" aria-label={labels.ariaLabel}>
      <Link className="brand" href="/dashboard">
        SocialLens BI
      </Link>
      <div className="nav-actions">
        <NavLinks items={items.map((item) => ({ href: item.href, label: labels[item.key] }))} />
        <LanguageSwitcher currentLocale={locale} labels={languageLabels} />
      </div>
    </nav>
  );
}
