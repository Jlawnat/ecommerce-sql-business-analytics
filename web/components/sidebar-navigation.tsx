"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, BookOpen, PackageCheck, UsersRound } from "lucide-react";

const destinations = [
  { label: "Executive overview", icon: BarChart3, href: "/" },
  { label: "Customer intelligence", icon: UsersRound, href: "/customer-intelligence" },
  { label: "Delivery & satisfaction", icon: PackageCheck, href: "/delivery-satisfaction" },
  { label: "Methodology", icon: BookOpen, href: "/methodology" },
];

export function SidebarNavigation({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  return (
    <nav aria-label="Evidence Lab sections" className="sidebar-nav">
      <p className="nav-group-label">Research views</p>
      <ul>
        {destinations.map(({ label, icon: Icon, href }) => {
          const current = href === pathname;
          return <li key={label}>
            {href ? (
              <Link href={href} aria-current={current ? "page" : undefined} className={`nav-item${current ? " is-current" : ""}`} onClick={onNavigate}>
                <Icon aria-hidden="true" size={17} strokeWidth={1.7} />
                <span>{label}</span>
              </Link>
            ) : (
              <span className="nav-item is-planned" aria-disabled="true" title="Planned after current checkpoint review">
                <Icon aria-hidden="true" size={17} strokeWidth={1.7} />
                <span>{label}</span>
                <span className="planned-label">Planned</span>
              </span>
            )}
          </li>;
        })}
      </ul>
    </nav>
  );
}
