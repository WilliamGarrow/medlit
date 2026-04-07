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
    <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-800 mb-3">
      {Icon && (
        <Icon
          size={18}
          className={iconColor || "text-gray-400"}
          strokeWidth={1.5}
        />
      )}
      {children}
    </h3>
  );
}
