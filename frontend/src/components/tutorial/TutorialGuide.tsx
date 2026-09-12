"use client";
import React from "react";
import Link from "next/link";
import { Home, Upload, Loader2, BookOpen, Mail } from "lucide-react";

type Paso = {
  titulo: string;
  descripcion: React.ReactNode;
  icon: React.ReactNode;
};

const pasos: Paso[] = [
  {
    titulo: "Ir a la página principal",
    descripcion: "Haz clic en 'INICIO' en la barra de navegación para regresar a la página principal en cualquier momento.",
    icon: <Home className="h-8 w-8 text-green-500" />,
  },
  {
    titulo: "Subir tu cartilla",
    descripcion: (
      <>
        Selecciona &apos;SUBIR CARTILLA&apos; en la barra de navegación. Haz clic en el botón para seleccionar tu archivo.
        <br />
        <span className="font-bold text-black">
          Solo se aceptan archivos en formato XLSX que sigan la plantilla establecida.
        </span>
        <br />
        Puedes descargar la plantilla aquí:{" "}
        <a
          href="/Plantilla_Cartilla.xlsx"
          download
          className="text-green-600 underline hover:text-green-800 font-semibold"
        >
          Descargar aquí
        </a>
        .
      </>
    ),
    icon: <Upload className="h-8 w-8 text-blue-500" />,
  },
  {
    titulo: "Esperar el procesamiento",
    descripcion: "La página procesará tu archivo. Espera unos segundos hasta que veas la confirmación de que el archivo fue subido correctamente.",
    icon: <Loader2 className="h-8 w-8 text-yellow-500 animate-spin" />,
  },
  {
    titulo: "Consultar la guía rápida",
    descripcion: "Si tienes dudas, vuelve a esta sección haciendo clic en 'GUÍA RÁPIDA'. Aquí encontrarás la guía paso a paso.",
    icon: <BookOpen className="h-8 w-8 text-pink-500" />,
  },
  {
    titulo: "Contactar soporte",
    descripcion: "Si necesitas ayuda adicional, haz clic en 'CONTÁCTANOS' para enviar tus preguntas o comentarios.",
    icon: <Mail className="h-8 w-8 text-red-500" />,
  },
];

const glosario = [
  {
    termino: "Barras de acero",
    definicion: "Elementos cilíndricos de acero utilizados como refuerzo en estructuras de concreto. Proveen resistencia a la tracción y ayudan a soportar cargas estructurales.",
  },
  {
    termino: "Diámetro de las barras",
    definicion: "Corresponde al grosor de la barra de acero, especificado en milímetros según la NSR-10. Generalmente se identifican por un número de barra (por ejemplo, #3, #4, #5), donde cada número corresponde a un diámetro estándar.",
  },
  {
    termino: "Peso de las barras por número de barra",
    definicion: "El peso por metro de cada barra depende de su número y está especificado en la NSR-10. Por ejemplo, una barra #4 pesa aproximadamente 0.668 kg/m. Esta información es fundamental para cálculos estructurales y de presupuesto.",
  },
  {
    termino: "Patrón de corte",
    definicion: "Esquema o secuencia que indica cómo deben cortarse las barras de acero para minimizar desperdicios y optimizar el uso del material.",
  },
  {
    termino: "Método Búfalo",
    definicion: "Técnica de optimización utilizada para determinar la mejor manera de cortar barras de acero, minimizando el desperdicio y maximizando la eficiencia en el uso del material.",
  },
  {
    termino: "Método rápido",
    definicion: "Ejecuta la optimización en menos tiempo, usando menos ciclos y población. Es útil para obtener resultados rápidos, aunque puede sacrificar algo de eficiencia.",
  },
  {
    termino: "Método balanceado",
    definicion: "Ofrece un equilibrio entre velocidad y eficiencia. Es la opción recomendada para la mayoría de los casos, ya que da buenos resultados en un tiempo razonable.",
  },
  {
    termino: "Método intensivo",
    definicion: "Busca la máxima eficiencia posible usando más ciclos y población, aunque tarde más tiempo en encontrar la mejor solución. Ideal cuando se quiere minimizar el desperdicio al máximo.",
  },
  {
    termino: "Cartilla de acero",
    definicion: "Documento (en XLSX) que contiene la información de las barras de acero a utilizar en un proyecto, incluyendo cantidades, longitudes y especificaciones técnicas.",
  },
  {
    termino: "N° de orden",
    definicion: "Número consecutivo que identifica cada registro o elemento de la lista.",
  },
  {
    termino: "Elemento",
    definicion: "Nombre o descripción del elemento estructural al que pertenece la barra, por ejemplo: viga, columna, losa, etc.",
  },
];

const faqs = [
  {
    pregunta: "¿Qué tipo de archivos puedo subir?",
    respuesta: "Puedes subir archivos únicamente en formato XLSX que sigan la plantilla proporcionada.",
  },
  {
    pregunta: "¿Cuánto tarda el procesamiento?",
    respuesta: "Normalmente solo unos segundos, dependiendo del tamaño del archivo.",
  },
];

export default function TutorialGuide() {
  return (
    <section className="max-w-6xl mx-auto mt-24 p-4 bg-white rounded-xl shadow-lg">
      <div className="flex flex-col md:flex-row gap-16">
        {/* Guía rápida - Izquierda */}
        <div className="md:w-1/2 flex flex-col">
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-gray-700 mb-6 text-center md:text-left">
              Pasos para utilizar la plataforma
            </h2>
            <div className="grid gap-8">
              {pasos.map((paso, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-5 bg-gray-50 rounded-lg p-5 shadow transition hover:scale-[1.02] hover:shadow-md"
                >
                  <div className="flex-shrink-0">{paso.icon}</div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-700 mb-1">
                      {idx + 1}. {paso.titulo}
                    </h3>
                    <p className="text-gray-600">{paso.descripcion}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        {/* Línea divisoria vertical */}
        <div className="hidden md:flex w-px bg-gray-300 mx-2 rounded-full"></div>
        {/* Glosario y FAQ - Derecha */}
        <div className="md:w-1/2 flex flex-col gap-12">
          {/* Glosario */}
          <div>
            <h2 className="text-2xl font-extrabold mb-4 tracking-wide text-center md:text-left"
                style={{
                  background: "linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent"
                }}>
              Glosario de Términos Clave
            </h2>
            <ul className="list-disc list-inside text-gray-600 space-y-3">
              {glosario.map((item, idx) => (
                <li key={idx}>
                  <span className="font-semibold text-gray-800">{item.termino}:</span> {item.definicion}
                </li>
              ))}
            </ul>
          </div>
          {/* FAQ */}
          <div>
            <h2 className="text-2xl font-extrabold mb-4 tracking-wide text-center md:text-left"
                style={{
                  background: "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent"
                }}>
              Preguntas Frecuentes (FAQ)
            </h2>
            <div className="space-y-4 text-gray-600">
              {faqs.map((faq, idx) => (
                <div key={idx}>
                  <span className="font-semibold text-gray-800">{faq.pregunta}</span>
                  <br />
                  {faq.respuesta}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <div className="mt-16 text-center text-base text-gray-500">
        ¿Tienes más dudas?{" "}
        <Link
          href="/contact-us"
          className="font-semibold text-green-600 underline hover:text-green-800 transition"
        >
          Escríbenos
        </Link>{" "}
        en la sección de contacto.
      </div>
    </section>
  );
}