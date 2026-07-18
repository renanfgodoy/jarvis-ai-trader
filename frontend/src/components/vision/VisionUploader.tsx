import { ImagePlus, RefreshCw, Trash2, UploadCloud } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface VisionUploaderProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
}

const ACCEPT = 'image/png,image/jpeg,image/webp';

export default function VisionUploader({ file, onFileChange, disabled = false }: VisionUploaderProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [imageSize, setImageSize] = useState<{ width: number; height: number } | null>(null);
  const [dragging, setDragging] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (!file) {
      setObjectUrl(null);
      setImageSize(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setObjectUrl(url);
    setImageSize(null);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  useEffect(() => {
    function onPaste(event: ClipboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target?.closest('input, textarea, [contenteditable="true"]')) {
        return;
      }
      const item = Array.from(event.clipboardData?.items ?? []).find((entry) => entry.type.startsWith('image/'));
      if (!item) {
        return;
      }
      const pasted = item.getAsFile();
      if (!pasted) {
        return;
      }
      event.preventDefault();
      onFileChange(pasted);
      setNotice('Imagem colada com sucesso.');
    }
    window.addEventListener('paste', onPaste);
    return () => window.removeEventListener('paste', onPaste);
  }, [onFileChange]);

  const chooseFile = (selected: File | null | undefined) => {
    if (!selected) {
      return;
    }
    onFileChange(selected);
    setNotice(null);
  };

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        if (!disabled) chooseFile(event.dataTransfer.files.item(0));
      }}
      className={`rounded-xl border p-4 transition ${
        dragging ? 'border-cyan-300 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03]'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        disabled={disabled}
        onChange={(event) => chooseFile(event.target.files?.item(0))}
      />
      {!file || !objectUrl ? (
        <button
          type="button"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
          className="flex min-h-[280px] w-full flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-white/15 bg-black/15 text-center"
        >
          <UploadCloud className="text-cyan-200" size={34} />
          <span className="text-sm font-black uppercase tracking-widest text-white">Selecionar print</span>
          <span className="max-w-md text-xs font-semibold leading-5 text-slate-400">
            Arraste uma imagem, clique para selecionar ou cole com Command + V / Control + V.
          </span>
        </button>
      ) : (
        <div className="space-y-3">
          <div className="overflow-hidden rounded-lg border border-white/10 bg-black/30">
            <img
              src={objectUrl}
              alt="Preview do print enviado"
              className="max-h-[420px] w-full object-contain"
              onLoad={(event) =>
                setImageSize({ width: event.currentTarget.naturalWidth, height: event.currentTarget.naturalHeight })
              }
            />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs font-semibold text-slate-300">
            <span>
              {file.name || 'Imagem colada'} · {(file.size / 1024 / 1024).toFixed(2)} MB
              {imageSize ? ` · ${imageSize.width}x${imageSize.height}` : ''}
            </span>
            <div className="flex gap-2">
              <button type="button" className="rounded-lg border border-white/10 px-3 py-2 text-white" onClick={() => inputRef.current?.click()}>
                <RefreshCw size={14} className="mr-2 inline" />
                Substituir
              </button>
              <button type="button" className="rounded-lg border border-red-300/20 px-3 py-2 text-red-200" onClick={() => onFileChange(null)}>
                <Trash2 size={14} className="mr-2 inline" />
                Remover
              </button>
            </div>
          </div>
        </div>
      )}
      {notice && (
        <p className="mt-3 flex items-center gap-2 text-xs font-bold text-cyan-200">
          <ImagePlus size={14} />
          {notice}
        </p>
      )}
    </div>
  );
}
