import Link from "next/link";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/content", label: "Content" },
  { href: "/sentiment", label: "Sentiment" },
  { href: "/competitors", label: "Competitors" },
  { href: "/posts", label: "Posts" },
  { href: "/data-health", label: "Data health" }
];

export function AppNav() {
  return (
    <nav className="app-nav" aria-label="Primary navigation">
      <Link className="brand" href="/dashboard">
        SocialLens BI
      </Link>
      <div className="nav-links">
        {items.map((item) => (
          <Link href={item.href} key={item.href}>
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
