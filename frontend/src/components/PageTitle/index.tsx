import type { ReactNode } from 'react';

export default function PageTitle({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return (
    <div className="panel p-4">
      <p className="eyebrow">{eyebrow}</p>
      <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
        <h2 className="text-2xl font-black text-white md:text-3xl">{title}</h2>
        {children}
      </div>
    </div>
  );
}
