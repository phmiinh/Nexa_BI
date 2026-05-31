"use client";

import { useRouter } from "next/navigation";
import type { Locale } from "@/lib/i18n";

type LanguageSwitcherProps = {
  currentLocale: Locale;
  labels: {
    label: string;
    english: string;
    vietnamese: string;
  };
};

export function LanguageSwitcher({ currentLocale, labels }: LanguageSwitcherProps) {
  const router = useRouter();

  function setLocale(locale: Locale) {
    document.cookie = `sociallens_locale=${locale}; path=/; max-age=31536000; samesite=lax`;
    router.refresh();
  }

  return (
    <div className="language-switcher" aria-label={labels.label}>
      <button
        aria-pressed={currentLocale === "en"}
        className={currentLocale === "en" ? "active" : ""}
        onClick={() => setLocale("en")}
        type="button"
      >
        {labels.english}
      </button>
      <button
        aria-pressed={currentLocale === "vi"}
        className={currentLocale === "vi" ? "active" : ""}
        onClick={() => setLocale("vi")}
        type="button"
      >
        {labels.vietnamese}
      </button>
    </div>
  );
}
