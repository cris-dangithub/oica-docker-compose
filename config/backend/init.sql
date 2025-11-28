-- OICA Database Schema
-- Migración: localStorage → PostgreSQL con versionamiento

-- Tabla principal de archivos subidos
CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    document_number VARCHAR(50), -- [DEPRECATED] Auto-rellenado para compatibilidad
    processing_status VARCHAR(20) DEFAULT 'processing',
    status_details VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comentarios para documentación
COMMENT ON TABLE uploaded_files IS 'Archivos Excel subidos por el usuario';
COMMENT ON COLUMN uploaded_files.processing_status IS 'Estados: uploaded, validating, validated, processing, generating_artifacts, completed, error_validation, error_processing, error_generation';
COMMENT ON COLUMN uploaded_files.status_details IS 'Mensaje descriptivo del estado actual (ej: "Ejecutando algoritmo genético gen 23/50...")';

-- Tabla de resultados del procesamiento (relación 1:N con uploaded_files)
CREATE TABLE IF NOT EXISTS processing_results (
    id SERIAL PRIMARY KEY,
    uploaded_file_id INTEGER NOT NULL REFERENCES uploaded_files(id) ON DELETE CASCADE,
    
    -- Versionamiento
    version_number INTEGER NOT NULL DEFAULT 1,
    
    -- UUID para directorio de almacenamiento (UUIDv4)
    storage_uuid VARCHAR(36) NOT NULL UNIQUE,
    
    -- Resultados del algoritmo genético (almacenados como JSONB)
    resultados JSONB NOT NULL,
    metricas JSONB NOT NULL,
    cartilla JSONB NOT NULL,
    
    -- Paths de artefactos generados en filestore
    -- Formato: filestore/{storage_uuid}/archivo.ext
    graph_image_path VARCHAR(500),
    pdf_path VARCHAR(500),
    excel_path VARCHAR(500),
    
    -- Estado del resultado (para manejar errores parciales)
    result_status VARCHAR(20) DEFAULT 'processing',
    error_message TEXT,
    
    -- Metadata del procesamiento
    perfil_usado VARCHAR(20),
    processing_time_seconds NUMERIC(10, 2),
    
    -- Versionado de plantilla PDF
    pdf_template_version VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- CONSTRAINT: Cada versión debe ser única por archivo
    UNIQUE(uploaded_file_id, version_number)
);

-- Comentarios para documentación
COMMENT ON TABLE processing_results IS 'Resultados de procesamiento con versionamiento. Cada archivo puede tener múltiples versiones.';
COMMENT ON COLUMN processing_results.storage_uuid IS 'UUID v4 único para directorio de almacenamiento. Evita colisiones entre versiones.';
COMMENT ON COLUMN processing_results.result_status IS 'Estados: completed, error_generation, processing';
COMMENT ON COLUMN processing_results.perfil_usado IS 'Perfil de optimización: rapido, balanceado, intensivo';
COMMENT ON COLUMN processing_results.pdf_template_version IS 'Versión de plantilla HTML usada para generar PDF (ej: v2.1.0)';

-- Índices para optimizar consultas
CREATE INDEX idx_uploaded_files_document_number ON uploaded_files(document_number);
CREATE INDEX idx_uploaded_files_status ON uploaded_files(processing_status);
CREATE INDEX idx_uploaded_files_created_at ON uploaded_files(created_at DESC);
CREATE INDEX idx_uploaded_files_file_name ON uploaded_files(file_name);

CREATE INDEX idx_processing_results_file_id ON processing_results(uploaded_file_id);
CREATE INDEX idx_processing_results_version ON processing_results(uploaded_file_id, version_number DESC);
CREATE INDEX idx_processing_results_status ON processing_results(result_status);
CREATE INDEX idx_processing_results_uuid ON processing_results(storage_uuid);
CREATE INDEX idx_processing_results_perfil ON processing_results(perfil_usado);
CREATE INDEX idx_processing_results_created_at ON processing_results(created_at DESC);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_uploaded_files_updated_at
    BEFORE UPDATE ON uploaded_files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_results_updated_at
    BEFORE UPDATE ON processing_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Información de inicialización
INSERT INTO uploaded_files (file_name, file_path, file_extension, document_number, processing_status, status_details)
VALUES ('_README.txt', '/dev/null', 'txt', '_SYSTEM_INIT', 'completed', 'Sistema inicializado correctamente')
ON CONFLICT (document_number) DO NOTHING;

-- Confirmar creación
DO $$
BEGIN
    RAISE NOTICE 'Schema OICA creado exitosamente';
    RAISE NOTICE 'Tablas: uploaded_files, processing_results';
    RAISE NOTICE 'Índices y triggers configurados';
END $$;
