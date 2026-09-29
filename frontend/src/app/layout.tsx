import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { Navbar } from '@/components/navbar';

const geistSans = Geist({
   variable: '--font-geist-sans',
   subsets: ['latin'],
});

const geistMono = Geist_Mono({
   variable: '--font-geist-mono',
   subsets: ['latin'],
});

export const metadata: Metadata = {
   title: {
      default: 'OICA — Optimización inteligente de cortes de acero',
      template: '%s — OICA',
   },
   description:
      'Planifica cortes de acero por etapas, reutiliza sobrantes y compara resultados de optimización.',
};

export default function RootLayout({
   children,
}: Readonly<{
   children: React.ReactNode;
}>) {
   return (
      <html lang="es">
         <body
            className={`${geistSans.variable} ${geistMono.variable} bg-surface text-content antialiased`}
         >
            <Navbar />
            <main className="min-h-screen pt-16">{children}</main>
         </body>
      </html>
   );
}
