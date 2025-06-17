-- Script SQL để tạo schema database cho Study Buddy
-- Chạy trong Supabase SQL Editor

-- 1. Tạo bảng session_documents để lưu tài liệu theo session
CREATE TABLE IF NOT EXISTS session_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL,
    user_id UUID NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    content TEXT NOT NULL,
    summary TEXT DEFAULT '',
    questions JSONB DEFAULT '[]'::jsonb,
    page_count INTEGER DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraints (nếu bảng chat_sessions đã tồn tại)
    CONSTRAINT fk_session_documents_session_id 
        FOREIGN KEY (session_id) 
        REFERENCES chat_sessions(id) 
        ON DELETE CASCADE
);

-- 2. Tạo bảng document_pages để lưu nội dung từng trang PDF
CREATE TABLE IF NOT EXISTS document_pages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_document_pages_document_id 
        FOREIGN KEY (document_id) 
        REFERENCES session_documents(id) 
        ON DELETE CASCADE,
    
    -- Unique constraint để tránh trùng lặp trang
    CONSTRAINT uk_document_pages_doc_page 
        UNIQUE (document_id, page_number)
);

-- 3. Tạo indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_session_documents_user_id ON session_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_session_documents_created_at ON session_documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_document_pages_document_id ON document_pages(document_id);
CREATE INDEX IF NOT EXISTS idx_document_pages_page_number ON document_pages(page_number);

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
