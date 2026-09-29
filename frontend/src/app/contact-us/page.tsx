import type { Metadata } from "next";
import { Mail, MapPin, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Field, Input, Textarea } from "@/components/ui/form-controls";

export const metadata: Metadata = { title: "Contacto" };

const equipo = [
  { nombre: "Lizeth Gasca", correo: "Lizethgasca990@gmail.com", ciudad: "Neiva, Huila" },
  { nombre: "Cristian Muñoz", correo: "Cristiandaniel8080@gmail.com", ciudad: "Neiva, Huila" },
];

export default function ContactUs() {
  return (
    <div className="mx-auto w-full max-w-wide px-4 py-10 sm:px-6 sm:py-12 lg:px-8">
      <header className="mb-8 max-w-narrow">
        <p className="mb-2 font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">Contacto</p>
        <h1 className="text-3xl font-semibold tracking-tight text-content sm:text-4xl">Contáctanos</h1>
        <p className="mt-3 text-base leading-7 text-content-muted">
          ¿Tienes dudas, sugerencias o necesitas soporte? Escríbenos.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.4fr] lg:items-start">
        <section aria-label="Equipo" className="space-y-4">
          {equipo.map(persona => (
            <Card key={persona.correo} className="flex items-start gap-4 p-5">
              <span
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-surface-interactive text-lg font-semibold text-content-brand"
                aria-hidden="true"
              >
                {persona.nombre[0]}
              </span>
              <div className="min-w-0">
                <p className="font-semibold text-content">{persona.nombre}</p>
                <p className="mt-2 flex items-center gap-2 text-sm text-content-muted">
                  <Mail className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <a href={`mailto:${persona.correo}`} className="break-all text-content-brand underline underline-offset-4">
                    {persona.correo}
                  </a>
                </p>
                <p className="mt-1 flex items-center gap-2 text-sm text-content-muted">
                  <MapPin className="h-4 w-4 shrink-0" aria-hidden="true" />
                  {persona.ciudad}
                </p>
              </div>
            </Card>
          ))}
        </section>

        <Card className="p-5 sm:p-6">
          <h2 className="text-lg font-semibold text-content">Envíanos un mensaje</h2>
          <p className="mt-1 text-sm text-content-muted">Todos los campos son obligatorios.</p>
          <form
            className="mt-5 space-y-4"
            action="https://formspree.io/f/xgvlrnje"//Link de Formspree
            method="POST"
          >
            <Field label="Nombre" htmlFor="contact-name">
              <Input id="contact-name" type="text" name="nombre" autoComplete="name" required />
            </Field>
            <Field label="Correo electrónico" htmlFor="contact-email">
              <Input id="contact-email" type="email" name="correo" autoComplete="email" required />
            </Field>
            <Field label="Mensaje" htmlFor="contact-message">
              <Textarea id="contact-message" name="mensaje" rows={5} required />
            </Field>
            <div className="flex justify-end">
              <Button type="submit">
                <Send className="h-4 w-4" aria-hidden="true" />
                Enviar mensaje
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
