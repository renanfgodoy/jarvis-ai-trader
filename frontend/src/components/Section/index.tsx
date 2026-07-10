import type { ReactNode } from 'react';

export default function Section({ title, children, action }: { title: string; children: ReactNode; action?: ReactNode }) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="eyebrow">{title}</p>
        {action}
      </div>
      <div className="mt-3">{children}</div>
    </div>
  );
}
