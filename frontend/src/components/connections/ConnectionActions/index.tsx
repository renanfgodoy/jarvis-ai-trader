import { FormEvent, useState } from 'react';
import { LogIn, LogOut, RefreshCw, RotateCcw } from 'lucide-react';
import ActionButton from '../../ActionButton';
import Card from '../../Card';

export default function ConnectionActions({
  connected,
  loading,
  onConnect,
  onSync,
  onRefresh,
  onDisconnect,
  feedback
}: {
  connected: boolean;
  loading: boolean;
  onConnect: (email: string, password: string, remember: boolean) => Promise<void>;
  onSync: () => Promise<void>;
  onRefresh: () => Promise<void>;
  onDisconnect: () => Promise<void>;
  feedback?: string | null;
}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (loading) return;
    await onConnect(email, password, remember);
    setPassword('');
  };

  return (
    <Card>
      <div>
        <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Ações</p>
        <h3 className="mt-1 text-lg font-black text-white">Controle da conexão</h3>
      </div>

      {!connected && (
        <form className="mt-5 space-y-3" onSubmit={submit}>
          <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">E-mail Polarium</label>
          <input className="login-input" value={email} onChange={(event) => setEmail(event.target.value)} type="email" placeholder="seu@email.com" required />
          <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Senha</label>
          <input className="login-input" value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="Senha da Polarium" required />
          <label className="flex items-center gap-2 text-xs text-slate-400">
            <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />
            Manter sessão no cache seguro do backend
          </label>
          <ActionButton className="w-full justify-center border-cyan-400/30 text-cyan-100 disabled:opacity-60" disabled={loading}>
            <LogIn size={14} /> {loading ? 'Conectando...' : 'Conectar'}
          </ActionButton>
        </form>
      )}

      {connected && (
        <div className="mt-5 grid gap-2 sm:grid-cols-2">
          <ActionButton type="button" onClick={onSync} disabled={loading} className="justify-center border-cyan-400/30 text-cyan-100 disabled:opacity-60">
            <RefreshCw size={14} /> Sincronizar
          </ActionButton>
          <ActionButton type="button" onClick={onRefresh} disabled={loading} className="justify-center text-slate-200 disabled:opacity-60">
            <RotateCcw size={14} /> Atualizar status
          </ActionButton>
          <ActionButton type="button" onClick={onDisconnect} disabled={loading} className="justify-center text-red-200 disabled:opacity-60 sm:col-span-2">
            <LogOut size={14} /> Desconectar
          </ActionButton>
        </div>
      )}

      {!connected && (
        <div className="mt-3">
          <ActionButton type="button" onClick={onRefresh} disabled={loading} className="w-full justify-center text-slate-200 disabled:opacity-60">
            <RotateCcw size={14} /> Atualizar status
          </ActionButton>
        </div>
      )}

      {feedback && <p className="mt-4 rounded-2xl border border-white/10 bg-white/[0.025] p-3 text-sm text-slate-300">{feedback}</p>}
    </Card>
  );
}
