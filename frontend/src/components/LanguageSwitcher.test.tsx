import { fireEvent, render, screen } from "@testing-library/react";

import { LanguageSwitcher } from "@/components/LanguageSwitcher";

const refresh = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ refresh })
}));

describe("LanguageSwitcher", () => {
  beforeEach(() => {
    refresh.mockClear();
    document.cookie = "sociallens_locale=; path=/; max-age=0";
  });

  it("marks the current locale and refreshes after selecting another locale", () => {
    render(
      <LanguageSwitcher
        currentLocale="en"
        labels={{ label: "Language", english: "EN", vietnamese: "VI" }}
      />
    );

    expect(screen.getByRole("button", { name: "EN" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "VI" })).toHaveAttribute("aria-pressed", "false");

    fireEvent.click(screen.getByRole("button", { name: "VI" }));

    expect(document.cookie).toContain("sociallens_locale=vi");
    expect(refresh).toHaveBeenCalledTimes(1);
  });
});
