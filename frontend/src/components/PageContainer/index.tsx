import type { ReactNode } from 'react';

export default function PageContainer({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={`mx-auto max-w-[1960px] space-y-3 p-3 2xl:p-4 ${className}`}>{children}</section>;
}
