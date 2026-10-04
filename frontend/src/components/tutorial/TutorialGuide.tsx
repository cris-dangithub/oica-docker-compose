import React from "react";
import Link from "next/link";
import { ChevronDown, Download } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type Paso = {
  titulo: string;
  descripcion: React.ReactNode;
};

// Contenido alineado con la plantilla, la UI actual y el Cap. 3 de la tesis.
const pasos: Paso[] = [
  {
    titulo: "Prepara la cartilla",
    descripcion: (
      <>
        Usa la plantilla con las columnas N° Orden, Elemento, N° de Barra, Longitud total (m), Cantidad,
        Grupo de Ejecución (opcional) y Masa total (kg). Se aceptan archivos XLSX o CSV.
      </>
    ),
  },
  {
    titulo: "Configura la optimización",
    descripcion: (
      <>
        En <Link href="/subir-cartilla" className="font-medium text-content-brand underline underline-offset-4">Configurar</Link>,
        carga la cartilla, elige el perfil y revisa el catálogo comercial, el inventario adicional y las condiciones físicas.
      </>
    ),
  },
  {
    titulo: "Estima e inicia",
    descripcion: "“Estimar tiempo” calcula un rango a partir de ejecuciones anteriores. Al iniciar, el progreso se actualiza en tiempo real.",
  },
  {
    titulo: "Revisa y descarga",
    descripcion: (
      <>
        En <Link href="/archivos" className="font-medium text-content-brand underline underline-offset-4">Proyectos</Link> descarga
        el Excel, el PDF, la gráfica y el inventario final. Reprocesar con otro perfil crea una nueva versión.
      </>
    ),
  },
  {
    titulo: "Reutiliza el inventario final",
    descripcion: "Puedes cargar el inventario final como inventario adicional de otro proyecto, después de verificar las existencias físicas.",
  },
];

const glosario = [
  {
    termino: "Barras de acero",
    definicion: "Elementos de acero utilizados como refuerzo en estructuras de concreto. Proveen resistencia a la tracción y ayudan a soportar cargas estructurales.",
  },
  {
    termino: "Número de barra",
    definicion: "Identifica el diámetro nominal según la NSR-10 (#3, #4, #5…). Por ejemplo, una barra #4 tiene 12.7 mm de diámetro y una masa de 0.994 kg/m.",
  },
  {
    termino: "Masa por metro lineal",
    definicion: "Masa de la barra por cada metro según su número. La hoja TablaBarras de la plantilla la usa para calcular la masa total; OICA rechaza masas inconsistentes.",
  },
  {
    termino: "Cartilla de acero",
    definicion: "Documento XLSX o CSV con los pedidos de barras de un proyecto: diámetros, longitudes, cantidades y masa.",
  },
  {
    termino: "N° de orden",
    definicion: "Número consecutivo que identifica cada registro o elemento de la lista.",
  },
  {
    termino: "Elemento",
    definicion: "Nombre o descripción del elemento estructural al que pertenece la barra, por ejemplo: viga, columna o losa.",
  },
  {
    termino: "Grupo de ejecución",
    definicion: "Etapa de obra a la que pertenece un pedido. Las etapas se procesan en orden numérico. Si la columna no existe, toda la cartilla es una sola etapa.",
  },
  {
    termino: "Catálogo comercial",
    definicion: "Longitudes de barra disponibles por diámetro (por defecto 6, 9 y 12 m). Una cantidad vacía significa disponibilidad ilimitada.",
  },
  {
    termino: "Inventario adicional",
    definicion: "Existencias finitas que pueden usarse desde la primera etapa. Se carga con las columnas diametro, longitud_m y cantidad.",
  },
  {
    termino: "Patrón de corte",
    definicion: "Esquema repetible de corte de una barra: de qué barra se parte, qué piezas se obtienen en cada etapa, qué sobra y cuántas veces se repite en el plan (patrón × repeticiones). Las barras cortadas de forma idéntica comparten patrón.",
  },
  {
    termino: "Nesting lineal",
    definicion: "Acomodo unidimensional de piezas a lo largo de barras. OICA lo presenta por patrones de corte; no realiza nesting bidimensional de piezas irregulares.",
  },
  {
    termino: "Pérdida por corte",
    definicion: "Material que se consume en cada separación. Referencias editables: disco 1 mm nominal y cizalla 0 mm idealizada.",
  },
  {
    termino: "Longitud mínima reutilizable",
    definicion: "Longitud a partir de la cual un saldo sigue siendo inventario útil. En modo automático se usa la menor longitud demandada por diámetro.",
  },
  {
    termino: "Inventario final",
    definicion: "Existencias no utilizadas y saldos reutilizables al terminar el proyecto, exportados con el mismo formato del inventario adicional.",
  },
  {
    termino: "Algoritmo genético",
    definicion: "Técnica de Inteligencia Artificial de la familia de la computación evolutiva: evoluciona una población de planes mediante selección por torneo, cruce, mutación y elitismo. Busca planes con poco desperdicio, sin garantizar que sean óptimos.",
  },
  {
    termino: "Cota inferior",
    definicion: "Desperdicio por debajo del cual ningún plan puede bajar, calculado con el enfoque de patrones de corte de Gilmore–Gomory. Mide la calidad del plan (la brecha); no lo construye ni demuestra optimalidad.",
  },
  {
    termino: "Desperdicio admisible",
    definicion: "Porcentaje máximo de desperdicio que define el usuario para su proyecto, por ejemplo el de su análisis de precios unitarios o su contrato. No se identificó un máximo normativo; OICA solo informa si el plan está dentro o lo excede.",
  },
];

const perfiles = [
  { nombre: "Rápido", poblacion: 20, generaciones: 30, estancamiento: 8, nota: "Menor tiempo de procesamiento." },
  { nombre: "Balanceado", poblacion: 50, generaciones: 100, estancamiento: 15, nota: "Recomendado para la mayoría de cartillas." },
  { nombre: "Profundo", poblacion: 100, generaciones: 200, estancamiento: 25, nota: "Mayor búsqueda, sin garantía de mejora." },
];

const faqs = [
  {
    pregunta: "¿Qué tipo de archivos puedo subir?",
    respuesta: "Cartillas en XLSX o CSV que sigan la estructura de la plantilla. El inventario adicional también se acepta en XLSX o CSV.",
  },
  {
    pregunta: "¿Cuánto tarda el procesamiento?",
    respuesta: "Depende del tamaño de la cartilla y del perfil. Usa “Estimar tiempo” para obtener un rango basado en ejecuciones anteriores; la espera en cola no se incluye.",
  },
  {
    pregunta: "¿El perfil profundo siempre da un mejor resultado?",
    respuesta: "No. Explora más soluciones y tarda más, pero no garantiza una mejora frente al perfil balanceado.",
  },
  {
    pregunta: "¿La pérdida por corte y el mínimo reutilizable son valores normativos?",
    respuesta: "No. Son supuestos editables del modelo; no representan mínimos legales ni una validación estructural.",
  },
  {
    pregunta: "¿Qué pasa con los resultados anteriores al reprocesar?",
    respuesta: "Cada reproceso crea una nueva versión con sus propios parámetros y su propio desperdicio admisible. La lista muestra la versión más reciente; en «Ver detalle» puedes comparar todas.",
  },
  {
    pregunta: "¿Puedo procesar barras #2?",
    respuesta: "El catálogo por defecto va de #3 a #18 y no incluye #2. Si tu cartilla tiene pedidos #2, agrega al catálogo las longitudes de #2 disponibles antes de procesar.",
  },
];

const secciones = [
  { id: "pasos", label: "Pasos" },
  { id: "perfiles", label: "Perfiles" },
  { id: "glosario", label: "Glosario" },
  { id: "preguntas", label: "Preguntas" },
];

export default function TutorialGuide() {
  return (
    <div className="mx-auto w-full max-w-wide px-4 py-10 sm:px-6 sm:py-12 lg:px-8">
      <header className="mb-8 max-w-narrow">
        <p className="mb-2 font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">Guía</p>
        <h1 className="text-3xl font-semibold tracking-tight text-content sm:text-4xl">Cómo usar OICA</h1>
        <p className="mt-3 text-base leading-7 text-content-muted">
          Pasos para optimizar una cartilla, términos clave y respuestas a las dudas más comunes.
        </p>
        <a href="/Plantilla_Cartilla.xlsx" download className={buttonVariants({ variant: "outline", className: "mt-5" })}>
          <Download className="h-4 w-4" aria-hidden="true" />
          Descargar plantilla de cartilla
        </a>
      </header>

      <div className="grid gap-8 lg:grid-cols-[14rem_1fr]">
        <nav aria-label="Secciones de la guía" className="lg:sticky lg:top-24 lg:self-start">
          <ul className="flex gap-2 overflow-x-auto pb-1 lg:flex-col lg:gap-1">
            {secciones.map(s => (
              <li key={s.id} className="shrink-0">
                <a
                  href={`#${s.id}`}
                  className="block rounded-md px-3 py-2 text-sm font-medium text-content-muted hover:bg-surface-interactive hover:text-content-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus"
                >
                  {s.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="min-w-0 space-y-12">
          <section id="pasos" aria-labelledby="pasos-title" className="scroll-mt-24">
            <h2 id="pasos-title" className="text-2xl font-semibold tracking-tight text-content">Pasos</h2>
            <ol className="mt-5 space-y-3">
              {pasos.map((paso, idx) => (
                <li key={paso.titulo}>
                  <Card className="flex gap-4 p-5">
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-status-info-border bg-status-info-bg font-mono text-sm font-semibold text-status-info-text">
                      {String(idx + 1).padStart(2, "0")}
                    </span>
                    <div>
                      <h3 className="font-semibold text-content">{paso.titulo}</h3>
                      <p className="mt-1 text-sm leading-6 text-content-muted">{paso.descripcion}</p>
                    </div>
                  </Card>
                </li>
              ))}
            </ol>
          </section>

          <section id="perfiles" aria-labelledby="perfiles-title" className="scroll-mt-24">
            <h2 id="perfiles-title" className="text-2xl font-semibold tracking-tight text-content">Perfiles de optimización</h2>
            <p className="mt-2 text-sm leading-6 text-content-muted">
              Cada perfil define el tamaño de la población, el máximo de generaciones y cuántas generaciones sin mejora detienen la búsqueda.
            </p>
            <Card className="mt-5 overflow-x-auto focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus" tabIndex={0} role="region" aria-label="Tabla de perfiles de optimización">
              <table className="w-full text-left text-sm">
                <caption className="sr-only">Parámetros de cada perfil</caption>
                <thead className="border-b border-line bg-surface-subtle text-xs font-semibold text-content-muted">
                  <tr>
                    <th scope="col" className="px-5 py-3">Perfil</th>
                    <th scope="col" className="px-4 py-3 text-right">Población</th>
                    <th scope="col" className="px-4 py-3 text-right">Generaciones</th>
                    <th scope="col" className="px-4 py-3 text-right">Estancamiento</th>
                    <th scope="col" className="px-5 py-3">Uso</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {perfiles.map(p => (
                    <tr key={p.nombre}>
                      <th scope="row" className="px-5 py-3 font-semibold text-content">{p.nombre}</th>
                      <td className="px-4 py-3 text-right font-mono tabular-nums">{p.poblacion}</td>
                      <td className="px-4 py-3 text-right font-mono tabular-nums">{p.generaciones}</td>
                      <td className="px-4 py-3 text-right font-mono tabular-nums">{p.estancamiento}</td>
                      <td className="min-w-48 px-5 py-3 text-content-muted">{p.nota}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          </section>

          <section id="glosario" aria-labelledby="glosario-title" className="scroll-mt-24">
            <h2 id="glosario-title" className="text-2xl font-semibold tracking-tight text-content">Glosario</h2>
            <dl className="mt-5 grid gap-3 md:grid-cols-2">
              {glosario.map(item => (
                <div key={item.termino} className="rounded-lg border border-line bg-surface-elevated p-4">
                  <dt className="font-semibold text-content">{item.termino}</dt>
                  <dd className="mt-1 text-sm leading-6 text-content-muted">{item.definicion}</dd>
                </div>
              ))}
            </dl>
          </section>

          <section id="preguntas" aria-labelledby="preguntas-title" className="scroll-mt-24">
            <h2 id="preguntas-title" className="text-2xl font-semibold tracking-tight text-content">Preguntas frecuentes</h2>
            <Card className="mt-5 divide-y divide-line">
              {faqs.map(faq => (
                <details key={faq.pregunta} className="group">
                  <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 font-medium text-content focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-line-focus">
                    {faq.pregunta}
                    <ChevronDown className="h-5 w-5 shrink-0 text-content-muted transition-transform duration-standard group-open:rotate-180" aria-hidden="true" />
                  </summary>
                  <p className="px-5 pb-4 text-sm leading-6 text-content-muted">{faq.respuesta}</p>
                </details>
              ))}
            </Card>
            <p className="mt-6 text-sm text-content-muted">
              ¿Tienes más dudas?{" "}
              <Link href="/contact-us" className="font-medium text-content-brand underline underline-offset-4">
                Escríbenos
              </Link>{" "}
              desde la sección de contacto.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
