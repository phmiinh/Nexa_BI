type PageHeaderProps = {
  title: string;
  eyebrow: string;
  description: string;
};

export function PageHeader({ title, eyebrow, description }: PageHeaderProps) {
  return (
    <header className="page-header">
      <span>{eyebrow}</span>
      <h1>{title}</h1>
      <p>{description}</p>
    </header>
  );
}
