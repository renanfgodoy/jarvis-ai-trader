import { LockKeyhole, ShieldCheck, Wifi } from 'lucide-react';
import { brand } from '../branding/brand';
import ActionButton from '../components/ActionButton';
import BrandLogo from '../components/BrandLogo';
import Card from '../components/Card';

export default function Login({ onEnter }: { onEnter: () => void }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#05070D] p-4 text-slate-200">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.13),transparent_34%),linear-gradient(180deg,#08111F,#05070D)]" />
      <Card className="w-full max-w-5xl">
        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="flex flex-col justify-between">
            <div>
              <BrandLogo />
              <p className="mt-8 text-[10px] font-black uppercase tracking-[0.32em] text-cyan-300">Modo Desenvolvimento</p>
              <h1 className="mt-3 text-4xl font-black text-white md:text-5xl">{brand.name}</h1>
              <p className="mt-3 text-2xl font-black text-cyan-200">{brand.tagline}</p>
              <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-400">{brand.descriptor}. Login visual reservado para desenvolvimento; autenticação real não foi implementada nesta Sprint.</p>
            </div>
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <LoginMetric icon={Wifi} label="Plataforma" value="Online" />
              <LoginMetric icon={ShieldCheck} label="Execução" value="DEMO" />
              <LoginMetric icon={LockKeyhole} label="Versão" value={`v${brand.version}`} />
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
            <div className="mb-5">
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Acesso visual</p>
              <h2 className="mt-1 text-xl font-black text-white">{brand.shortName} Workspace</h2>
            </div>
            <form className="space-y-3" onSubmit={(event) => { event.preventDefault(); onEnter(); }}>
              <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Operador</label>
              <input className="login-input" defaultValue={brand.operatorName} />
              <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Senha visual</label>
              <input className="login-input" type="password" placeholder="••••••••" />
              <ActionButton className="w-full justify-center border-cyan-400/30 text-cyan-100">
                <LockKeyhole size={14} /> Entrar no modo desenvolvimento
              </ActionButton>
            </form>
            <p className="mt-4 text-xs leading-relaxed text-slate-500">Este formulário é apenas uma porta visual para a interface local. Não representa autenticação segura em produção.</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

function LoginMetric({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
      <Icon className="text-cyan-300" size={18} />
      <p className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-black text-white">{value}</p>
    </div>
  );
}
