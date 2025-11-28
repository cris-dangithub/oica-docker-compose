-- Migración: Remover UNIQUE constraint de document_number
-- Fecha: 2025-11-27
-- Razón: Permitir reprocesamiento de archivos con mismo nombre

BEGIN;

-- 1. Remover constraint UNIQUE de document_number
ALTER TABLE uploaded_files DROP CONSTRAINT IF EXISTS uploaded_files_document_number_key;

-- 2. Hacer document_number opcional (nullable)
ALTER TABLE uploaded_files ALTER COLUMN document_number DROP NOT NULL;

-- 3. Agregar índice en file_name para búsquedas (si no existe)
CREATE INDEX IF NOT EXISTS idx_uploaded_files_file_name ON uploaded_files(file_name);

-- 4. Actualizar registros existentes: si document_number está vacío, usar file_name
UPDATE uploaded_files 
SET document_number = REGEXP_REPLACE(file_name, '\.[^.]*$', '') 
WHERE document_number IS NULL OR document_number = '';

-- 5. Agregar comentario explicativo
COMMENT ON COLUMN uploaded_files.document_number IS 
'[DEPRECATED] Campo legacy. Usar file_name como identificador principal. 
Auto-rellenado con nombre de archivo sin extensión para compatibilidad.';

COMMIT;

-- Verificar cambios
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'uploaded_files' 
AND column_name IN ('file_name', 'document_number');
