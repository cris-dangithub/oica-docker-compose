import { API_URL } from '@/lib/api';
/**
 * Página de gestión de archivos procesados.
 * Muestra tabla completa con filtros, descargas y acciones.
 */
import FilesTable from '@/components/FilesTable';

export default function ArchivosPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Archivos Procesados
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Gestiona todos los archivos cargados, consulta estados y descarga resultados.
          </p>
        </div>

        <FilesTable apiUrl={API_URL} />
      </div>
    </div>
  );
}
