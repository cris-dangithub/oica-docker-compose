import type { Metadata } from 'next';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { API_URL } from '@/lib/api';
import { buttonVariants } from '@/components/ui/button';
/**
 * Página de gestión de archivos procesados.
 * Muestra tabla completa con filtros, descargas y acciones.
 */
import FilesTable from '@/components/FilesTable';

export const metadata: Metadata = { title: 'Proyectos' };

export default function ArchivosPage() {
  return (
    <div className="mx-auto w-full max-w-wide px-4 py-10 sm:px-6 sm:py-12 lg:px-8">
      <header className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div className="max-w-narrow">
          <p className="mb-2 font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">
            Historial
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-content sm:text-4xl">
            Proyectos procesados
          </h1>
          <p className="mt-3 text-base leading-7 text-content-muted">
            Consulta el estado de cada cartilla, compara versiones y descarga sus resultados.
          </p>
        </div>
        <Link href="/subir-cartilla" className={buttonVariants({ className: 'self-start sm:self-auto' })}>
          <Plus className="h-4 w-4" aria-hidden="true" />
          Nueva optimización
        </Link>
      </header>

      <FilesTable apiUrl={API_URL} />
    </div>
  );
}
