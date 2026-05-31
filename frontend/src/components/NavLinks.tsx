"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = {
  href: string;
  label: string;
};

type NavLinksProps = {
  items: NavItem[];
};

export function NavLinks({ items }: NavLinksProps) {
  const pathname = usePathname();

  return (
    <div className="nav-links">
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link aria-current={active ? "page" : undefined} className={active ? "active" : ""} href={item.href} key={item.href}>
            {item.label}
          </Link>
        );
      })}
    </div>
  );
}
