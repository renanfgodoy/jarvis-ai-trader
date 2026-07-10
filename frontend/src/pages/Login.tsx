import { LockKeyhole } from 'lucide-react';
import { brand } from '../branding/brand';
import ActionButton from '../components/ActionButton';
import BrandLogo from '../components/BrandLogo';
import Card from '../components/Card';

export default function Login({ onEnter }: { onEnter: () => void }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#05051f] p-4 text-slate-200">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.14),transparent_32%),linear-gradient(180deg,#060626,#05051f)]" />
      <Card className="w-full max-w-md">
        <div className="text-center">
          <div className="mb-4 flex justify-center">
            <BrandLogo />
          </div>
          <p className="eyebrow">Modo Desenvolvimento</p>
          <h1 className="mt-2 text-3xl font-black text-white">{brand.name}</h1>
          <p className="mt-2 text-sm text-slate-400">{brand.subtitle}. Layout de login reservado. Sem autenticação nesta Sprint.</p>
        </div>
        <form className="mt-5 space-y-3" onSubmit={(event) => { event.preventDefault(); onEnter(); }}>
          <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Usuário</label>
          <input className="login-input" defaultValue={brand.operatorName} />
          <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Senha</label>
          <input className="login-input" type="password" placeholder="••••••••" />
          <ActionButton className="w-full border-cyan-400/30 text-cyan-100">
            <LockKeyhole size={14} /> Entrar
          </ActionButton>
        </form>
      </Card>
    </div>
  );
}
