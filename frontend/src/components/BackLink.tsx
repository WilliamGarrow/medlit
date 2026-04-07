import Link from "next/link";

export default function BackLink({
  href,
  label,
}: {
  href: string;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="inline-flex items-center text-sm text-brand-accent hover:text-teal-700"
    >
      &larr; {label}
    </Link>
  );
}
