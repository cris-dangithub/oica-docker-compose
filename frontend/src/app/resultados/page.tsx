import { redirect } from 'next/navigation';

// Los artefactos se descargan por versión desde la tabla; el flujo localStorage
// anterior llamaba a un endpoint que ya no existe en el servidor de producción.
export default function ResultadosPage() {
   redirect('/archivos');
}
