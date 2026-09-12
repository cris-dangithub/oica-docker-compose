"use client";
import React from "react";

export default function ContactUs() {
  return (
    <div className="flex flex-col items-center bg-white pt-12 pb-8 min-h-screen">
      <div className="w-full max-w-2xl px-4">
        <h1 className="text-3xl font-bold mb-6 text-black text-center">Contáctanos</h1>
        <p className="mb-6 text-center text-gray-700 font-medium">
          ¿Tienes dudas, sugerencias o necesitas soporte? ¡Escríbenos!
        </p>
        <div className="bg-white p-6 rounded shadow-md flex flex-col md:flex-row items-center gap-8 justify-center">
          {/* Persona 1 */}
          <div className="flex-1 flex flex-col items-center">
            <div className="w-20 h-20 rounded-full bg-amber-300 flex items-center justify-center mb-2">
              <span className="text-3xl font-bold text-amber-900">L</span>
            </div>
            <div className="text-center">
              <div className="font-bold text-black">Lizeth Gasca</div>
              <div className="text-black text-sm">Email: Lizethgasca990@gmail.com</div>
              <div className="text-black text-sm">Ciudad: Neiva, Huila</div>
            </div>
          </div>
          {/* Persona 2 */}
          <div className="flex-1 flex flex-col items-center">
            <div className="w-20 h-20 rounded-full bg-indigo-400 flex items-center justify-center mb-2">
              <span className="text-3xl font-bold text-indigo-50">C</span>
            </div>
            <div className="text-center">
              <div className="font-bold text-black">Cristian Muñoz</div>
              <div className="text-black text-sm">Email: Cristiandaniel8080@gmail.com</div>
              <div className="text-black text-sm">Ciudad: Neiva, Huila</div>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded shadow-md mt-4">
          <form
            className="flex flex-col gap-4"
            action="https://formspree.io/f/xgvlrnje"//Link de Formspree
            method="POST"
          >
            <input
              type="text"
              name="nombre"
              placeholder="Tu nombre"
              className="border-2 border-green-500 p-2 rounded focus:outline-none focus:ring-2 focus:ring-green-400 bg-gray-50 text-black placeholder:text-gray-600"
              required
            />
            <input
              type="email"
              name="correo"
              placeholder="Tu correo"
              className="border-2 border-green-500 p-2 rounded focus:outline-none focus:ring-2 focus:ring-green-400 bg-gray-50 text-black placeholder:text-gray-600"
              required
            />
            <textarea
              name="mensaje"
              placeholder="Tu mensaje"
              className="border-2 border-green-500 p-2 rounded focus:outline-none focus:ring-2 focus:ring-green-400 bg-gray-50 text-black placeholder:text-gray-600"
              rows={4}
              required
            />
            <button
              type="submit"
              className="bg-green-500 text-white py-2 rounded hover:bg-green-600"
            >
              Enviar
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}