'use client';
/**
 * Campo decimal (spec 002, enmienda 2: FR-034). Acepta coma o punto en cualquier navegador,
 * conserva lo que el usuario escribe mientras edita y solo emite números válidos.
 */
import * as React from 'react';
import { leerDecimal } from '@/components/file-detail/types';
import { Input } from './form-controls';

interface DecimalInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'value' | 'onChange' | 'type'> {
   value: number | null;
   onValue: (value: number) => void;
}

// Se muestra con punto decimal (FR-032); al escribir se acepta coma o punto (FR-034).
const mostrar = (value: number | null) => (value == null ? '' : String(value));

function DecimalInput({ value, onValue, ...props }: DecimalInputProps) {
   const [texto, setTexto] = React.useState(() => mostrar(value));
   const emitido = React.useRef(value);
   // Si el valor cambia desde fuera (por ejemplo, al quitar una fila), se vuelve a mostrar.
   React.useEffect(() => {
      if (value !== emitido.current) {
         emitido.current = value;
         setTexto(mostrar(value));
      }
   }, [value]);
   const invalido = texto.trim() !== '' && leerDecimal(texto) === null;
   return (
      <Input
         type="text"
         inputMode="decimal"
         autoComplete="off"
         value={texto}
         aria-invalid={invalido ? true : undefined}
         onChange={event => {
            setTexto(event.target.value);
            const numero = leerDecimal(event.target.value);
            if (numero !== null) {
               emitido.current = numero;
               onValue(numero);
            }
         }}
         {...props}
      />
   );
}

export { DecimalInput };
