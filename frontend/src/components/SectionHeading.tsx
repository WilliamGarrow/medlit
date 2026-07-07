"use client";

import { HeartIcon, PillIcon, TestTubeIcon, FileTextIcon, UsersIcon } from "./Icons";

const ICONS: Record<string, React.ElementType> = {
  heart: HeartIcon,
  pill: PillIcon,
  "test-tube": TestTubeIcon,
  "file-text": FileTextIcon,
  users: UsersIcon,
};

export default function SectionHeading({
  icon,
  iconColor,
  children,
}: {
  icon: string;
  iconColor?: string;
  children: React.ReactNode;
}) {
  const Icon = ICONS[icon];
  return (
    <h3 className="flex items-center gap-2.5 mb-4">
      {Icon && (
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white border border-brand-line shadow-sm">
          <Icon
            size={16}
            className={iconColor || "text-gray-400"}
            strokeWidth={1.75}
          />
        </span>
      )}
      <span className="font-display text-xl font-semibold tracking-tight text-brand-navy flex items-baseline gap-2">
        {children}
      </span>
    </h3>
  );
}
