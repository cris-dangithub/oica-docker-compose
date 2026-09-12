"use client";
import React from "react";
import Image from "next/image";

export default function Inicio() {
  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-green-100 via-white to-green-200 px-4">
      {/* Imagen de fondo */}
      <Image
        src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"
        alt="Barras de acero apiladas"
        className="absolute inset-0 w-full h-full object-cover opacity-20 pointer-events-none"
        style={{ zIndex: 0 }}
        fill
        sizes="100vw"
        priority
      />
      {/* Contenido principal */}
      <div className="relative max-w-2xl w-full text-center py-16" style={{ zIndex: 1 }}>
        <h1 className="text-4xl md:text-5xl font-extrabold text-green-700 mb-6 drop-shadow">
          Bienvenido a OICA Steel Cutting Optimizer
        </h1>
        <p className="text-lg md:text-xl text-gray-700 mb-8 font-medium">
          Optimiza el corte de acero, reduce desperdicios y maximiza tu producción.<br />
          Nuestra plataforma te ayuda a planificar cortes de manera eficiente, fácil y rápida.<br />
          <span className="text-green-600 font-semibold">¡Haz que cada centímetro cuente!</span>
        </p>
        <div className="flex flex-col md:flex-row gap-4 justify-center">
          <a
            href="/contact-us"
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded font-bold shadow transition"
          >
            Contáctanos
          </a>
          <a
            href="/subir-cartilla"
            className="bg-white border-2 border-green-500 text-green-700 px-6 py-3 rounded font-bold shadow hover:bg-green-50 transition"
          >
            Probar Optimizador
          </a>
        </div>
      </div>
    </div>
  );
}