"use client";
import Link from 'next/link';
import { Menu, Ruler, X } from 'lucide-react';
import { usePathname } from "next/navigation";
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

const navigation = [
   { href: '/', label: 'Inicio' },
   { href: '/subir-cartilla', label: 'Configurar' },
   { href: '/archivos', label: 'Proyectos' },
   { href: '/tutorial', label: 'Guía' },
   { href: '/contact-us', label: 'Contacto' },
];

export function Navbar() {
   const pathname = usePathname();
   const [open, setOpen] = useState(false);

   useEffect(() => setOpen(false), [pathname]);

   const navLink = (href: string, label: string, mobile = false) => {
      const active = pathname === href;
      return (
         <Link
            key={href}
            href={href}
            aria-current={active ? 'page' : undefined}
            className={cn(
               'rounded-md text-sm font-medium transition-colors duration-standard focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus focus-visible:ring-offset-2',
               mobile ? 'block px-3 py-3' : 'px-3 py-2',
               active
                  ? 'bg-surface-interactive text-content-brand'
                  : 'text-content-muted hover:bg-surface-subtle hover:text-content'
            )}
         >
            {label}
         </Link>
      );
   };

   return (
      <header className="fixed inset-x-0 top-0 z-50 border-b border-line bg-surface-elevated/95 backdrop-blur">
         <div className="mx-auto flex h-16 max-w-wide items-center justify-between px-4 sm:px-6 lg:px-8">
            <Link
               href="/"
               className="flex min-h-11 items-center gap-3 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus"
               aria-label="OICA, ir al inicio"
            >
               <span className="flex h-9 w-9 items-center justify-center rounded-md bg-action-primary text-content-inverse">
                  <Ruler className="h-5 w-5" aria-hidden="true" />
               </span>
               <span className="flex items-baseline gap-2">
                  <span className="text-lg font-bold tracking-tight text-content">OICA</span>
                  <span className="hidden font-mono text-xs uppercase tracking-widest text-content-muted sm:inline">
                     Material Intelligence
                  </span>
               </span>
            </Link>

            <nav className="hidden items-center gap-1 lg:flex" aria-label="Navegación principal">
               {navigation.map(item => navLink(item.href, item.label))}
            </nav>

            <button
               type="button"
               className="inline-flex h-11 w-11 items-center justify-center rounded-md border border-line-strong bg-surface-elevated text-content lg:hidden"
               aria-label={open ? 'Cerrar menú principal' : 'Abrir menú principal'}
               aria-expanded={open}
               aria-controls="mobile-navigation"
               onClick={() => setOpen(value => !value)}
            >
               {open ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
            </button>
         </div>

         {open && (
            <nav
               id="mobile-navigation"
               className="border-t border-line bg-surface-elevated px-4 py-3 shadow-overlay lg:hidden"
               aria-label="Navegación móvil"
            >
               <div className="mx-auto max-w-wide space-y-1">
                  {navigation.map(item => navLink(item.href, item.label, true))}
               </div>
            </nav>
         )}
      </header>
   );
}
