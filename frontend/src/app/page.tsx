import Link from 'next/link';
import { ArrowRight, FileSpreadsheet, FolderOpen, Layers3, Recycle, Ruler, Scissors, SlidersHorizontal } from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { decimal } from '@/components/file-detail/types';

const pasos = [
  { n: '01', titulo: 'Carga la cartilla', detalle: 'XLSX o CSV con pedidos, diámetros, longitudes, cantidades y grupo de ejecución.' },
  { n: '02', titulo: 'Configura las condiciones', detalle: 'Catálogo comercial, inventario disponible, pérdida por corte y mínimo reutilizable.' },
  { n: '03', titulo: 'Descarga el plan de corte', detalle: 'Excel completo, PDF, gráfica e inventario final para el siguiente proyecto.' },
];

const capacidades = [
  { icon: Ruler, titulo: 'Barras comerciales', detalle: 'Longitudes de 6, 9 y 12 m por diámetro, con disponibilidad editable.' },
  { icon: Layers3, titulo: 'Corte por etapas', detalle: 'Los grupos de ejecución se procesan en orden y comparten sus saldos.' },
  { icon: Recycle, titulo: 'Reutilización de saldos', detalle: 'Los sobrantes útiles pasan a etapas posteriores o al inventario final.' },
  { icon: Scissors, titulo: 'Pérdida por corte', detalle: 'Reserva material por separación según el proceso: disco o cizalla.' },
  { icon: SlidersHorizontal, titulo: 'Perfiles del algoritmo', detalle: 'Rápido, balanceado o profundo, según el tiempo disponible.' },
  { icon: FolderOpen, titulo: 'Versiones trazables', detalle: 'Cada reproceso guarda sus parámetros y resultados por separado.' },
];

// Diagrama ilustrativo de una barra de 12 m (no corresponde a un resultado real).
const tramos = [
  { m: 4.2, tipo: 'pieza' },
  { m: 3.5, tipo: 'pieza' },
  { m: 2.8, tipo: 'pieza' },
  { m: 1.5, tipo: 'saldo' },
] as const;

export default function Inicio() {
  return (
    <div className="mx-auto w-full max-w-wide px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
      <section className="grid items-center gap-10 lg:grid-cols-2 lg:gap-16" aria-labelledby="hero-title">
        <div>
          <p className="mb-3 font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">
            Optimización de cortes de acero
          </p>
          <h1 id="hero-title" className="text-4xl font-semibold tracking-tight text-content sm:text-5xl">
            Planifica el corte de barras con menos desperdicio
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-content-muted">
            OICA usa algoritmos genéticos para distribuir las piezas de una cartilla en barras
            comerciales, respetando etapas de obra y reutilizando los saldos disponibles.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/subir-cartilla" className={buttonVariants({ size: 'lg' })}>
              Configurar optimización
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
            <Link href="/tutorial" className={buttonVariants({ size: 'lg', variant: 'outline' })}>
              Ver la guía
            </Link>
          </div>
        </div>

        <Card className="p-5 sm:p-6" aria-labelledby="diagram-title">
          <div className="flex items-center justify-between gap-4">
            <p id="diagram-title" className="text-sm font-semibold text-content">Patrón de corte</p>
            <span className="font-mono text-xs text-content-muted">Ejemplo ilustrativo</span>
          </div>
          <p className="mt-1 text-xs text-content-muted">Barra #4 · 12 m</p>
          <div className="mt-5 flex h-12 overflow-hidden rounded-md border border-line-strong" role="img"
            aria-label="Barra de 12 metros dividida en piezas de 4.2, 3.5 y 2.8 metros y un saldo reutilizable de 1.5 metros">
            {tramos.map((t, i) => (
              <div
                key={i}
                style={{ width: `${(t.m / 12) * 100}%` }}
                className={t.tipo === 'pieza'
                  ? 'flex items-center justify-center border-r-2 border-surface-elevated bg-data-primary font-mono text-xs font-semibold text-content-inverse'
                  : 'flex items-center justify-center bg-status-success-bg font-mono text-xs font-semibold text-status-success-text'}
              >
                {decimal(t.m, 1)}
              </div>
            ))}
          </div>
          <div className="mt-2 flex justify-between font-mono text-xs text-content-muted" aria-hidden="true">
            <span>0 m</span><span>6 m</span><span>12 m</span>
          </div>
          <dl className="mt-5 grid grid-cols-3 gap-2">
            {[
              ['3', 'piezas'],
              ['1.5 m', 'saldo reutilizable'],
              ['0 m', 'descarte'],
            ].map(([valor, etiqueta]) => (
              <div key={etiqueta} className="flex flex-col rounded-md border border-line bg-surface-interactive p-3">
                <dt className="order-2 mt-1 text-xs text-content-muted">{etiqueta}</dt>
                <dd className="font-mono text-lg font-semibold tabular-nums text-content-brand">{valor}</dd>
              </div>
            ))}
          </dl>
          <div className="mt-4 flex flex-wrap gap-4 text-xs text-content-muted">
            <span className="flex items-center gap-2"><span className="h-3 w-3 rounded-sm bg-data-primary" aria-hidden="true" />Pieza demandada</span>
            <span className="flex items-center gap-2"><span className="h-3 w-3 rounded-sm border border-status-success-border bg-status-success-bg" aria-hidden="true" />Saldo para etapas posteriores</span>
          </div>
        </Card>
      </section>

      <section className="mt-20" aria-labelledby="flujo-title">
        <h2 id="flujo-title" className="text-2xl font-semibold tracking-tight text-content">Cómo funciona</h2>
        <ol className="mt-6 grid gap-4 md:grid-cols-3">
          {pasos.map(p => (
            <li key={p.n}>
              <Card className="h-full p-5 sm:p-6">
                <span className="flex h-9 w-9 items-center justify-center rounded-md border border-status-info-border bg-status-info-bg font-mono text-sm font-semibold text-status-info-text">
                  {p.n}
                </span>
                <h3 className="mt-4 font-semibold text-content">{p.titulo}</h3>
                <p className="mt-2 text-sm leading-6 text-content-muted">{p.detalle}</p>
              </Card>
            </li>
          ))}
        </ol>
      </section>

      <section className="mt-20" aria-labelledby="capacidades-title">
        <h2 id="capacidades-title" className="text-2xl font-semibold tracking-tight text-content">Qué considera el modelo</h2>
        <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {capacidades.map(({ icon: Icon, titulo, detalle }) => (
            <li key={titulo} className="flex gap-4 rounded-lg border border-line bg-surface-elevated p-5">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-surface-interactive text-content-brand">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <h3 className="font-semibold text-content">{titulo}</h3>
                <p className="mt-1 text-sm leading-6 text-content-muted">{detalle}</p>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-20" aria-labelledby="cta-title">
        <Card className="flex flex-col gap-6 bg-surface-interactive p-6 sm:p-8 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-4">
            <FileSpreadsheet className="mt-1 h-6 w-6 shrink-0 text-content-brand" aria-hidden="true" />
            <div>
              <h2 id="cta-title" className="text-xl font-semibold text-content">¿Primera vez?</h2>
              <p className="mt-1 text-sm leading-6 text-content-muted">
                Descarga la plantilla de cartilla y revisa la guía antes de cargar tu proyecto.
              </p>
            </div>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <a href="/Plantilla_Cartilla.xlsx" download className={buttonVariants({ variant: 'outline' })}>
              Descargar plantilla
            </a>
            <Link href="/archivos" className={buttonVariants({ variant: 'secondary' })}>
              Ver proyectos
            </Link>
          </div>
        </Card>
      </section>
    </div>
  );
}
