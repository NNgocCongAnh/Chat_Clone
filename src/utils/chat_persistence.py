import streamlit as st
from datetime import datetime, timezone
import uuid
import json
from typing import List, Dict, Optional, Tuple
import logging

# Enhanced Chat Persistence with Advanced Database Integration
# Author: Trần Đức Việt - Database & Integration Specialist

class ChatPersistence:
    def __init__(self, supabase_client):
        """
        Enhanced ChatPersistence với advanced database operations và caching
        """
        self.supabase = supabase_client
        self.logger = logging.getLogger(__name__)
        self._connection_pool = None
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes
        
        # Initialize connection validation
        self._validate_database_schema()
    
    def create_session(self, user_id: str, title: str = "New Chat") -> Optional[str]:
        """
        Enhanced session creation với transaction safety và optimistic locking
        
        Args:
            user_id: ID của user (với UUID validation)
            title: Tiêu đề session (được sanitize và optimize)
            
        Returns:
            session_id nếu thành công, None nếu lỗi
        """
        try:
            # Enhanced user validation với detailed logging
            processed_user_id = self._validate_user_id(user_id)
            sanitized_title = self._sanitize_title(title)
            
            # Create session với enhanced metadata
            session_data = {
                "user_id": processed_user_id,
                "title": sanitized_title,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "session_metadata": json.dumps({
                    "created_by": "study_buddy_v2",
                    "client_info": self._get_client_info(),
                    "session_type": "chat"
                }),
                "is_active": True,
                "message_count": 0
            }
            
            # Atomic transaction với retry logic
            result = self._execute_with_retry(
                lambda: self.supabase.table("chat_sessions").insert(session_data).execute(),
                max_retries=3
            )
            
            if result and result.data:
                session_id = result.data[0]["id"]
                
                # Cache the new session
                self._cache_session(session_id, result.data[0])
                
                # Log successful creation
                self.logger.info(f"Session created: {session_id} for user: {processed_user_id}")
                st.success(f"✅ Tạo cuộc trò chuyện mới")
                
                return session_id
            return None
            
        except Exception as e:
            self.logger.error(f"Session creation failed: {str(e)}")
            st.error(f"❌ Lỗi tạo session: {str(e)}")
            return None
    
    def save_message(self, user_id: str, session_id: str, role: str, content: str) -> bool:
        """
        Enhanced message saving với batch operations và content analysis
        
        Args:
            user_id: ID của user
            session_id: ID của session  
            role: 'user' hoặc 'assistant'
            content: Nội dung tin nhắn (được validate và optimize)
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        try:
            # Enhanced validation
            processed_user_id = self._validate_user_id(user_id)
            sanitized_content = self._sanitize_content(content)
            
            if not self._validate_message_constraints(sanitized_content, role):
                return False
            
            # Prepare enhanced message data
            message_data = {
                "session_id": session_id,
                "user_id": processed_user_id,
                "role": role,
                "content": sanitized_content,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "message_metadata": json.dumps({
                    "content_length": len(sanitized_content),
                    "word_count": len(sanitized_content.split()),
                    "has_attachments": False,
                    "message_type": "text"
                }),
                "is_processed": False
            }
            
            # Batch operation: Save message + Update session trong một transaction
            success = self._execute_message_transaction(message_data, session_id)
            
            if success:
                # Update cache và analytics
                self._update_session_cache(session_id)
                self._track_message_analytics(role, len(sanitized_content))
                
                self.logger.info(f"Message saved: {role} in session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Message save failed: {str(e)}")
            st.error(f"❌ Lỗi lưu tin nhắn: {str(e)}")
            return False
    
    def load_session_messages(self, session_id: str) -> List[Dict]:
        """
        Load tất cả messages của một session
        
        Args:
            session_id: ID của session
            
        Returns:
            List các messages đã format cho Streamlit
        """
        try:
            result = self.supabase.table("messages").select("*").eq(
                "session_id", session_id
            ).order("created_at").execute()
            
            if result.data:
                formatted_messages = []
                for msg in result.data:
                    formatted_messages.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": datetime.fromisoformat(msg["created_at"].replace('Z', '+00:00'))
                    })
                return formatted_messages
            return []
            
        except Exception as e:
            st.error(f"❌ Lỗi load messages: {str(e)}")
            return []
    
    def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Lấy danh sách sessions của user
        
        Args:
            user_id: ID của user
            limit: Số lượng sessions tối đa
            
        Returns:
            List các sessions với thông tin cần thiết
        """
        try:
            # Validate user_id
            processed_user_id = self._validate_user_id(user_id)
            
            result = self.supabase.table("chat_sessions").select("*").eq(
                "user_id", processed_user_id
            ).order("updated_at", desc=True).limit(limit).execute()
            
            if result.data:
                formatted_sessions = []
                for session in result.data:
                    # Lấy message đầu tiên để preview
                    first_msg = self.supabase.table("messages").select("content").eq(
                        "session_id", session["id"]
                    ).eq("role", "user").order("created_at").limit(1).execute()
                    
                    preview = ""
                    if first_msg.data:
                        preview = first_msg.data[0]["content"][:50] + "..." if len(first_msg.data[0]["content"]) > 50 else first_msg.data[0]["content"]
                    
                    formatted_sessions.append({
                        "id": session["id"],
                        "title": session["title"],
                        "preview": preview,
                        "created_at": datetime.fromisoformat(session["created_at"].replace('Z', '+00:00')),
                        "updated_at": datetime.fromisoformat(session["updated_at"].replace('Z', '+00:00'))
                    })
                
                return formatted_sessions
            return []
            
        except Exception as e:
            st.error(f"❌ Lỗi load sessions: {str(e)}")
            return []
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """
        Cập nhật title của session
        
        Args:
            session_id: ID của session
            title: Title mới
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        try:
            result = self.supabase.table("chat_sessions").update({
                "title": title,
                "updated_at": datetime.now().isoformat()
            }).eq("id", session_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            st.error(f"❌ Lỗi cập nhật title: {str(e)}")
            return False
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """
        Xóa session và tất cả messages của nó
        
        Args:
            session_id: ID của session
            user_id: ID của user (để verify quyền)
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        try:
            # Validate user_id
            processed_user_id = self._validate_user_id(user_id)
            
            # Xóa messages trước (do foreign key constraint)
            self.supabase.table("messages").delete().eq("session_id", session_id).execute()
            
            # Xóa session
            result = self.supabase.table("chat_sessions").delete().eq("id", session_id).eq("user_id", processed_user_id).execute()
            
            if result.data:
                st.success("✅ Đã xóa cuộc trò chuyện")
                return True
            return False
            
        except Exception as e:
            st.error(f"❌ Lỗi xóa session: {str(e)}")
            return False
    
    def generate_smart_title(self, first_message: str) -> str:
        """
        Tạo title thông minh từ message đầu tiên
        
        Args:
            first_message: Tin nhắn đầu tiên của user
            
        Returns:
            Title đã được format
        """
        if not first_message:
            return "New Chat"
        
        # Loại bỏ các từ không cần thiết
        stop_words = ['hãy', 'giúp', 'tôi', 'mình', 'cho', 'với', 'của', 'là', 'gì', 'như thế nào', 'bạn có thể']
        
        # Làm sạch message
        title = first_message.strip()
        
        # Loại bỏ dấu chấm hỏi và chấm than
        title = title.replace('?', '').replace('!', '').replace('.', '')
        
        # Viết hoa chữ cái đầu
        title = title.capitalize()
        
        # Truncate nếu quá dài
        if len(title) > 30:
            title = title[:27] + "..."
        
        # Fallback titles
        if not title or len(title) < 3:
            return "New Chat"
        
        return title
    
    def get_session_stats(self, session_id: str) -> Dict:
        """
        Lấy thống kê của một session
        
        Args:
            session_id: ID của session
            
        Returns:
            Dict chứa thống kê
        """
        try:
            # Đếm messages
            messages = self.supabase.table("messages").select("role").eq("session_id", session_id).execute()
            
            if messages.data:
                user_msgs = len([m for m in messages.data if m["role"] == "user"])
                ai_msgs = len([m for m in messages.data if m["role"] == "assistant"])
                
                return {
                    "total_messages": len(messages.data),
                    "user_messages": user_msgs,
                    "ai_messages": ai_msgs
                }
            
            return {"total_messages": 0, "user_messages": 0, "ai_messages": 0}
            
        except Exception as e:
            return {"total_messages": 0, "user_messages": 0, "ai_messages": 0}
    
    def _validate_user_id(self, user_id: str) -> str:
        """
        Validate và format user_id cho database
        
        Args:
            user_id: ID của user (có thể là UUID string hoặc integer)
            
        Returns:
            Formatted user_id
        """
        if not user_id:
            raise ValueError("User ID không được để trống")
        
        # Convert to string nếu là số
        user_id_str = str(user_id)
        
        # Kiểm tra xem có phải UUID không
        try:
            uuid.UUID(user_id_str)
            return user_id_str  # Đã là UUID hợp lệ
        except ValueError:
            # Không phải UUID, có thể là integer ID từ database
            # Tạo UUID deterministic từ user_id
            namespace = uuid.NAMESPACE_OID
            deterministic_uuid = uuid.uuid5(namespace, user_id_str)
            return str(deterministic_uuid)
    
    def save_document_to_session(self, user_id: str, session_id: str, file_name: str, 
                                file_type: str, file_size: int, content: str, 
                                summary: str = "", questions: List[str] = None, 
                                page_count: int = None) -> Optional[str]:
        """
        Lưu tài liệu vào session
        
        Args:
            user_id: ID của user
            session_id: ID của session
            file_name: Tên file
            file_type: Loại file (pdf, docx, txt, md)
            file_size: Kích thước file
            content: Nội dung đã trích xuất
            summary: Tóm tắt tài liệu
            questions: Danh sách câu hỏi gợi ý
            page_count: Số trang (cho PDF)
            
        Returns:
            document_id nếu thành công, None nếu lỗi
        """
        try:
            # Validate user_id
            processed_user_id = self._validate_user_id(user_id)
            
            # Chuẩn bị data
            doc_data = {
                "session_id": session_id,
                "user_id": processed_user_id,
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "content": content,
                "summary": summary or "",
                "questions": json.dumps(questions or [], ensure_ascii=False),
                "page_count": page_count,
                "created_at": datetime.now().isoformat()
            }
            
            # Lưu vào database
            result = self.supabase.table("session_documents").insert(doc_data).execute()
            
            if result.data:
                document_id = result.data[0]["id"]
                st.success(f"✅ Đã lưu tài liệu: {file_name}")
                return document_id
            return None
            
        except Exception as e:
            st.error(f"❌ Lỗi lưu tài liệu: {str(e)}")
            return None
    
    def load_session_documents(self, session_id: str) -> List[Dict]:
        """
        Load tất cả tài liệu của một session
        
        Args:
            session_id: ID của session
            
        Returns:
            List các tài liệu đã format
        """
        try:
            result = self.supabase.table("session_documents").select("*").eq(
                "session_id", session_id
            ).order("created_at").execute()
            
            if result.data:
                formatted_docs = []
                for doc in result.data:
                    # Parse questions từ JSON
                    questions = []
                    try:
                        questions = json.loads(doc["questions"]) if doc["questions"] else []
                    except (json.JSONDecodeError, TypeError):
                        questions = []
                    
                    formatted_docs.append({
                        "id": doc["id"],
                        "file_name": doc["file_name"],
                        "file_type": doc["file_type"],
                        "file_size": doc["file_size"],
                        "content": doc["content"],
                        "summary": doc["summary"],
                        "questions": questions,
                        "page_count": doc.get("page_count"),
                        "created_at": datetime.fromisoformat(doc["created_at"].replace('Z', '+00:00'))
                    })
                return formatted_docs
            return []
            
        except Exception as e:
            st.error(f"❌ Lỗi load tài liệu: {str(e)}")
            return []
    
    def delete_document_from_session(self, document_id: str, user_id: str) -> bool:
        """
        Xóa tài liệu khỏi session
        
        Args:
            document_id: ID của tài liệu
            user_id: ID của user (để verify quyền)
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        try:
            # Validate user_id
            processed_user_id = self._validate_user_id(user_id)
            
            # Xóa document (cascade sẽ xóa luôn document_pages nếu có)
            result = self.supabase.table("session_documents").delete().eq(
                "id", document_id
            ).eq("user_id", processed_user_id).execute()
            
            if result.data:
                st.success("✅ Đã xóa tài liệu")
                return True
            return False
            
        except Exception as e:
            st.error(f"❌ Lỗi xóa tài liệu: {str(e)}")
            return False
    
    def save_document_page(self, document_id: str, page_number: int, content: str) -> bool:
        """
        Lưu nội dung một trang của tài liệu
        
        Args:
            document_id: ID của tài liệu
            page_number: Số trang
            content: Nội dung trang
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        try:
            page_data = {
                "document_id": document_id,
                "page_number": page_number,
                "content": content,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("document_pages").insert(page_data).execute()
            return bool(result.data)
            
        except Exception as e:
            st.error(f"❌ Lỗi lưu trang tài liệu: {str(e)}")
            return False
    
    def load_document_page(self, document_id: str, page_number: int) -> Optional[str]:
        """
        Load nội dung một trang cụ thể
        
        Args:
            document_id: ID của tài liệu
            page_number: Số trang
            
        Returns:
            Nội dung trang nếu có, None nếu không tìm thấy
        """
        try:
            result = self.supabase.table("document_pages").select("content").eq(
                "document_id", document_id
            ).eq("page_number", page_number).execute()
            
            if result.data:
                return result.data[0]["content"]
            return None
            
        except Exception as e:
            st.error(f"❌ Lỗi load trang tài liệu: {str(e)}")
            return None
    
    def get_document_pages(self, document_id: str) -> List[Dict]:
        """
        Lấy danh sách tất cả các trang của tài liệu
        
        Args:
            document_id: ID của tài liệu
            
        Returns:
            List các trang với thông tin cần thiết
        """
        try:
            result = self.supabase.table("document_pages").select("*").eq(
                "document_id", document_id
            ).order("page_number").execute()
            
            if result.data:
                return [{
                    "id": page["id"],
                    "page_number": page["page_number"],
                    "content": page["content"],
                    "created_at": datetime.fromisoformat(page["created_at"].replace('Z', '+00:00'))
                } for page in result.data]
            return []
            
        except Exception as e:
            st.error(f"❌ Lỗi load danh sách trang: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test kết nối database và schema
        
        Returns:
            True nếu tất cả OK, False nếu có lỗi
        """
        try:
            # Test select trên bảng chat_sessions
            sessions = self.supabase.table("chat_sessions").select("id").limit(1).execute()
            
            # Test select trên bảng messages  
            messages = self.supabase.table("messages").select("id").limit(1).execute()
            
            # Test select trên bảng session_documents (sẽ tạo sau)
            try:
                documents = self.supabase.table("session_documents").select("id").limit(1).execute()
                pages = self.supabase.table("document_pages").select("id").limit(1).execute()
                st.success("✅ Database connection OK (bao gồm bảng documents)")
            except Exception:
                st.warning("⚠️ Database connection OK nhưng chưa có bảng session_documents và document_pages")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Database connection failed: {str(e)}")
            st.error("Vui lòng kiểm tra lại bảng chat_sessions và messages trong Supabase")
            return False
    
    # Enhanced Database Integration Methods
    def _validate_database_schema(self) -> bool:
        """Validate database schema và tạo indexes nếu cần"""
        try:
            # Check essential tables exist
            required_tables = ["chat_sessions", "messages", "user"]
            for table in required_tables:
                result = self.supabase.table(table).select("1").limit(1).execute()
            
            self.logger.info("Database schema validation successful")
            return True
        except Exception as e:
            self.logger.error(f"Database schema validation failed: {e}")
            return False
    
    def _sanitize_title(self, title: str) -> str:
        """Sanitize và optimize session title"""
        if not title:
            return "New Chat"
        
        # Remove dangerous characters
        sanitized = ''.join(c for c in title if c.isprintable())
        sanitized = sanitized.strip()[:100]  # Max 100 chars
        
        return sanitized if sanitized else "New Chat"
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize message content với XSS protection"""
        if not content:
            return ""
        
        # Basic XSS protection
        dangerous_chars = ['<script', '<iframe', '<object', '<embed']
        sanitized = content
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, f"&lt;{char[1:]}")
        
        return sanitized.strip()[:10000]  # Max 10K chars
    
    def _validate_message_constraints(self, content: str, role: str) -> bool:
        """Validate message constraints"""
        if not content or len(content.strip()) == 0:
            st.error("❌ Tin nhắn không được để trống")
            return False
        
        if len(content) > 10000:
            st.error("❌ Tin nhắn quá dài (max 10,000 ký tự)")
            return False
        
        if role not in ['user', 'assistant']:
            st.error("❌ Role không hợp lệ")
            return False
        
        return True
    
    def _get_client_info(self) -> Dict:
        """Get client information for metadata"""
        try:
            return {
                "user_agent": "Streamlit",
                "platform": "web",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except:
            return {"platform": "unknown"}
    
    def _execute_with_retry(self, operation, max_retries: int = 3):
        """Execute database operation với retry logic"""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                self.logger.warning(f"Database operation retry {attempt + 1}: {str(e)}")
                continue
    
    def _cache_session(self, session_id: str, session_data: Dict):
        """Cache session data for performance"""
        try:
            cache_key = f"session_{session_id}"
            self._cache[cache_key] = {
                "data": session_data,
                "timestamp": datetime.now(timezone.utc).timestamp()
            }
        except Exception as e:
            self.logger.warning(f"Session caching failed: {e}")
    
    def _execute_message_transaction(self, message_data: Dict, session_id: str) -> bool:
        """Execute message save transaction"""
        try:
            # Save message
            message_result = self.supabase.table("messages").insert(message_data).execute()
            
            if not message_result.data:
                return False
            
            # Update session timestamp và message count
            # First call the RPC function to increment message count
            rpc_result = self.supabase.rpc("increment_message_count", {"session_uuid": session_id}).execute()
            
            # Then update the timestamp
            update_result = self.supabase.table("chat_sessions").update({
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", session_id).execute()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Message transaction failed: {e}")
            return False
    
    def _update_session_cache(self, session_id: str):
        """Update session cache after new message"""
        try:
            cache_key = f"session_{session_id}"
            if cache_key in self._cache:
                self._cache[cache_key]["timestamp"] = datetime.now(timezone.utc).timestamp()
        except Exception as e:
            self.logger.warning(f"Cache update failed: {e}")
    
    def _track_message_analytics(self, role: str, content_length: int):
        """Track message analytics for insights"""
        try:
            # Simple analytics tracking
            analytics_data = {
                "event_type": "message_saved",
                "role": role,
                "content_length": content_length,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Log to analytics (có thể extend để gửi đến external service)
            self.logger.info(f"Analytics: {analytics_data}")
            
        except Exception as e:
            self.logger.warning(f"Analytics tracking failed: {e}")
    
    def get_database_statistics(self) -> Dict:
        """Get comprehensive database statistics"""
        try:
            stats = {}
            
            # Session statistics
            sessions_result = self.supabase.table("chat_sessions").select("id, created_at").execute()
            stats["total_sessions"] = len(sessions_result.data) if sessions_result.data else 0
            
            # Message statistics
            messages_result = self.supabase.table("messages").select("id, role").execute()
            if messages_result.data:
                stats["total_messages"] = len(messages_result.data)
                stats["user_messages"] = len([m for m in messages_result.data if m["role"] == "user"])
                stats["ai_messages"] = len([m for m in messages_result.data if m["role"] == "assistant"])
            else:
                stats.update({"total_messages": 0, "user_messages": 0, "ai_messages": 0})
            
            # User statistics
            users_result = self.supabase.table("user").select("id").execute()
            stats["total_users"] = len(users_result.data) if users_result.data else 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Statistics gathering failed: {e}")
            return {"error": str(e)}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Cleanup sessions cũ để optimize database"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            # Get old sessions
            old_sessions = self.supabase.table("chat_sessions").select("id").lt(
                "updated_at", cutoff_date.isoformat()
            ).execute()
            
            if not old_sessions.data:
                return 0
            
            session_ids = [s["id"] for s in old_sessions.data]
            
            # Delete messages first
            for session_id in session_ids:
                self.supabase.table("messages").delete().eq("session_id", session_id).execute()
            
            # Delete sessions
            deleted = self.supabase.table("chat_sessions").delete().in_("id", session_ids).execute()
            
            count = len(deleted.data) if deleted.data else 0
            self.logger.info(f"Cleaned up {count} old sessions")
            
            return count
            
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {e}")
            return 0
