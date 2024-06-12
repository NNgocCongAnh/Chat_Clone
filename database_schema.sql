-- Enhanced Database Schema for Study Buddy v2.0
-- Author: Trần Đức Việt - Database & Integration Specialist
-- Advanced PostgreSQL schema với performance optimization và data integrity

-- ================================
-- SECTION 1: ENHANCED CORE TABLES
-- ================================

-- 1. Enhanced session_documents table với advanced features
CREATE TABLE IF NOT EXISTS session_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL,
    user_id UUID NOT NULL,
    file_name TEXT NOT NULL CHECK (length(file_name) <= 255),
    file_type TEXT NOT NULL CHECK (file_type IN ('pdf', 'docx', 'txt', 'md')),
    file_size BIGINT DEFAULT 0 CHECK (file_size >= 0),
    content TEXT NOT NULL,
    summary TEXT DEFAULT '',
    questions JSONB DEFAULT '[]'::jsonb,
    page_count INTEGER DEFAULT NULL CHECK (page_count IS NULL OR page_count > 0),
    
    -- Enhanced metadata fields
    file_hash TEXT,  -- SHA256 hash để detect duplicates
    processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    processing_metadata JSONB DEFAULT '{}'::jsonb,
    content_language TEXT DEFAULT 'vi',
    content_encoding TEXT DEFAULT 'utf-8',
    
    -- Enhanced timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Soft delete support
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign key constraints
    CONSTRAINT fk_session_documents_session_id 
        FOREIGN KEY (session_id) 
        REFERENCES chat_sessions(id) 
        ON DELETE CASCADE,
    
    -- Unique constraint cho file hash để tránh duplicate
    CONSTRAINT uk_session_documents_file_hash 
        UNIQUE (user_id, file_hash)
);

-- 2. Enhanced document_pages table với advanced content management
CREATE TABLE IF NOT EXISTS document_pages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID NOT NULL,
    page_number INTEGER NOT NULL CHECK (page_number > 0),
    content TEXT NOT NULL,
    
    -- Enhanced page metadata
    page_hash TEXT,  -- Hash của page content
    word_count INTEGER DEFAULT 0,
    char_count INTEGER DEFAULT 0,
    has_images BOOLEAN DEFAULT FALSE,
    has_tables BOOLEAN DEFAULT FALSE,
    
    -- OCR and processing info
    ocr_confidence DECIMAL(5,2),  -- OCR confidence score (0.00-100.00)
    processing_time_ms INTEGER,    -- Time taken to process this page
    extraction_method TEXT DEFAULT 'text' CHECK (extraction_method IN ('text', 'ocr', 'hybrid')),
    
    -- Content analysis
    language_detected TEXT DEFAULT 'vi',
    content_type TEXT DEFAULT 'text' CHECK (content_type IN ('text', 'table', 'image', 'mixed')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_document_pages_document_id 
        FOREIGN KEY (document_id) 
        REFERENCES session_documents(id) 
        ON DELETE CASCADE,
    
    -- Enhanced unique constraint
    CONSTRAINT uk_document_pages_doc_page 
        UNIQUE (document_id, page_number)
);

-- 3. New table: document_analytics để track usage patterns
CREATE TABLE IF NOT EXISTS document_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID NOT NULL,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    
    -- Analytics data
    event_type TEXT NOT NULL CHECK (event_type IN ('view', 'chat', 'search', 'download', 'share')),
    page_number INTEGER,
    query_text TEXT,
    response_time_ms INTEGER,
    
    -- Context information
    client_info JSONB DEFAULT '{}'::jsonb,
    user_agent TEXT,
    ip_address INET,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign keys
    CONSTRAINT fk_document_analytics_document_id 
        FOREIGN KEY (document_id) 
        REFERENCES session_documents(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_document_analytics_session_id 
        FOREIGN KEY (session_id) 
        REFERENCES chat_sessions(id) 
        ON DELETE CASCADE
);

-- 4. New table: document_embeddings để support vector search
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID NOT NULL,
    page_number INTEGER,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    
    -- Content và embedding
    chunk_text TEXT NOT NULL,
    embedding_vector VECTOR(1536),  -- OpenAI ada-002 embedding size
    
    -- Metadata
    chunk_size INTEGER NOT NULL,
    chunk_overlap INTEGER DEFAULT 0,
    embedding_model TEXT DEFAULT 'text-embedding-ada-002',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key
    CONSTRAINT fk_document_embeddings_document_id 
        FOREIGN KEY (document_id) 
        REFERENCES session_documents(id) 
        ON DELETE CASCADE,
    
    -- Unique constraint
    CONSTRAINT uk_document_embeddings_doc_page_chunk 
        UNIQUE (document_id, page_number, chunk_index)
);

-- ================================
-- SECTION 2: ADVANCED INDEXING STRATEGY
-- ================================

-- Enhanced indexes cho session_documents
CREATE INDEX IF NOT EXISTS idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_session_documents_user_id ON session_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_session_documents_created_at ON session_documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_session_documents_file_type ON session_documents(file_type);
CREATE INDEX IF NOT EXISTS idx_session_documents_processing_status ON session_documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_session_documents_file_hash ON session_documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_session_documents_soft_delete ON session_documents(is_deleted, user_id);

-- Composite indexes cho complex queries
CREATE INDEX IF NOT EXISTS idx_session_documents_user_status_created 
    ON session_documents(user_id, processing_status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_session_documents_session_type_created 
    ON session_documents(session_id, file_type, created_at DESC);

-- Enhanced indexes cho document_pages
CREATE INDEX IF NOT EXISTS idx_document_pages_document_id ON document_pages(document_id);
CREATE INDEX IF NOT EXISTS idx_document_pages_page_number ON document_pages(page_number);
CREATE INDEX IF NOT EXISTS idx_document_pages_extraction_method ON document_pages(extraction_method);
CREATE INDEX IF NOT EXISTS idx_document_pages_content_type ON document_pages(content_type);

-- Composite index cho page search
CREATE INDEX IF NOT EXISTS idx_document_pages_doc_page_created 
    ON document_pages(document_id, page_number, created_at DESC);

-- Full-text search index cho page content
CREATE INDEX IF NOT EXISTS idx_document_pages_content_fts 
    ON document_pages USING gin(to_tsvector('vietnamese', content));

-- Indexes cho document_analytics
CREATE INDEX IF NOT EXISTS idx_document_analytics_document_id ON document_analytics(document_id);
CREATE INDEX IF NOT EXISTS idx_document_analytics_user_id ON document_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_document_analytics_event_type ON document_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_document_analytics_created_at ON document_analytics(created_at DESC);

-- Time-series index cho analytics
CREATE INDEX IF NOT EXISTS idx_document_analytics_time_series 
    ON document_analytics(user_id, event_type, created_at DESC);

-- Indexes cho document_embeddings  
CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id ON document_embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_page_number ON document_embeddings(page_number);

-- Vector similarity search index (requires pgvector extension)
-- CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector 
--     ON document_embeddings USING ivfflat(embedding_vector vector_cosine_ops) WITH (lists = 100);

-- 4. Tạo trigger để tự động update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_session_documents_updated_at 
    BEFORE UPDATE ON session_documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 5. Tạo RLS (Row Level Security) policies để bảo mật
ALTER TABLE session_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_pages ENABLE ROW LEVEL SECURITY;

-- Policy cho session_documents: user chỉ thấy documents của mình
CREATE POLICY "Users can view own session documents" ON session_documents
    FOR SELECT USING (user_id = auth.uid()::text::uuid);

CREATE POLICY "Users can insert own session documents" ON session_documents
    FOR INSERT WITH CHECK (user_id = auth.uid()::text::uuid);

CREATE POLICY "Users can update own session documents" ON session_documents
    FOR UPDATE USING (user_id = auth.uid()::text::uuid);

CREATE POLICY "Users can delete own session documents" ON session_documents
    FOR DELETE USING (user_id = auth.uid()::text::uuid);

-- Policy cho document_pages: user chỉ thấy pages của documents thuộc về mình
CREATE POLICY "Users can view own document pages" ON document_pages
    FOR SELECT USING (
        document_id IN (
            SELECT id FROM session_documents 
            WHERE user_id = auth.uid()::text::uuid
        )
    );

CREATE POLICY "Users can insert own document pages" ON document_pages
    FOR INSERT WITH CHECK (
        document_id IN (
            SELECT id FROM session_documents 
            WHERE user_id = auth.uid()::text::uuid
        )
    );

CREATE POLICY "Users can update own document pages" ON document_pages
    FOR UPDATE USING (
        document_id IN (
            SELECT id FROM session_documents 
            WHERE user_id = auth.uid()::text::uuid
        )
    );

CREATE POLICY "Users can delete own document pages" ON document_pages
    FOR DELETE USING (
        document_id IN (
            SELECT id FROM session_documents 
            WHERE user_id = auth.uid()::text::uuid
        )
    );

-- 6. Tạo function helper để lấy thống kê documents
CREATE OR REPLACE FUNCTION get_user_document_stats(user_uuid UUID)
RETURNS TABLE (
    total_documents BIGINT,
    total_pages BIGINT,
    pdf_count BIGINT,
    docx_count BIGINT,
    other_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_documents,
        COALESCE(SUM(page_count), 0) as total_pages,
        COUNT(*) FILTER (WHERE file_type = 'pdf') as pdf_count,
        COUNT(*) FILTER (WHERE file_type = 'docx') as docx_count,
        COUNT(*) FILTER (WHERE file_type NOT IN ('pdf', 'docx')) as other_count
    FROM session_documents 
    WHERE user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. Tạo function để dọn dẹp documents cũ (optional)
CREATE OR REPLACE FUNCTION cleanup_old_documents(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM session_documents 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. Tạo view để query dễ dàng hơn
CREATE OR REPLACE VIEW user_documents_with_stats AS
SELECT 
    sd.*,
    (SELECT COUNT(*) FROM document_pages dp WHERE dp.document_id = sd.id) as actual_page_count,
    (SELECT COUNT(*) FROM messages m WHERE m.session_id = sd.session_id) as message_count
FROM session_documents sd;

-- Kết thúc script
-- Chạy script này trong Supabase SQL Editor để tạo đầy đủ schema
