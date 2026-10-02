import type { Metadata } from 'next';
import FileDetail from '@/components/file-detail/FileDetail';

export const metadata: Metadata = { title: 'Detalle del proyecto' };

export default async function ArchivoDetallePage({ params }: { params: Promise<{ id: string }> }) {
   const { id } = await params;
   return <FileDetail id={id} />;
}
