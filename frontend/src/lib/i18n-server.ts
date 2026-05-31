import { cookies } from "next/headers";
import { defaultLocale, isLocale, type Locale } from "@/lib/i18n";

const localeCookie = "sociallens_locale";

export async function getRequestLocale(): Promise<Locale> {
  const cookieStore = await cookies();
  const value = cookieStore.get(localeCookie)?.value;
  return isLocale(value) ? value : defaultLocale;
}
