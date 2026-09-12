-- Compatibilidad con instalaciones anteriores.
ALTER TABLE uploaded_files DROP CONSTRAINT IF EXISTS uploaded_files_document_number_key;
ALTER TABLE uploaded_files ALTER COLUMN document_number DROP NOT NULL;
