import { API_URL } from '@/lib/api';
import React from "react";

export default function Resultados({ resultados, metricas, columns, document_number }) {
  // Función para descargar el PDF
  const descargarPDF = () => {
    fetch(`${API_URL}/descargar-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resultados,
        metricas,
        columnas: columns,
        document_number,
      }),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Error al generar el PDF");
        return response.blob();
      })
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `plan_corte_${document_number || "descarga"}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch((error) => {
        alert("No se pudo generar el PDF: " + error.message);
      });
  };

  return (
    <div style={{ textAlign: "center", marginTop: "60px" }}>
      <h2>¡Análisis completado!</h2>
      <button
        style={{
          fontSize: "1.2rem",
          padding: "20px 40px",
          margin: "40px auto",
          display: "block",
          background: "#4caf50",
          color: "#fff",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
        }}
        onClick={descargarPDF}
      >
        Descargar PDF
      </button>
      {/* Puedes mostrar un resumen aquí si quieres */}
      <p>Descarga tu reporte optimizado en PDF.</p>
    </div>
  );
}