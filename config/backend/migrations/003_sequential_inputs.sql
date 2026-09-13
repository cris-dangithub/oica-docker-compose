-- Instantáneas por carga y versión. NULL identifica registros históricos.
ALTER TABLE uploaded_files ADD COLUMN execution_config JSONB;
ALTER TABLE uploaded_files ADD COLUMN active_task_id VARCHAR(160);
ALTER TABLE uploaded_files ADD COLUMN active_profile VARCHAR(20);
ALTER TABLE processing_results ADD COLUMN execution_config JSONB;
ALTER TABLE processing_results ADD COLUMN inventory_path VARCHAR(500);
