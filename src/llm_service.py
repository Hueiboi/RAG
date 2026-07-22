from src.config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

def get_llm() -> ChatGroq:
    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key
    )
    
def get_prompt() -> ChatPromptTemplate:
    template = (
        """Bạn là một trợ lý AI chuyên trả lời câu hỏi dựa trên tài liệu được cung cấp.

        NGUYÊN TẮC:
        - Chỉ trả lời dựa trên ngữ cảnh bên dưới, không dùng kiến thức bên ngoài.
        - Nếu không tìm thấy thông tin: "Tôi không tìm thấy thông tin này trong tài liệu được cung cấp."
        - Nếu câu hỏi mơ hồ: yêu cầu người dùng cung cấp thêm thông tin cụ thể.
        - Nếu câu hỏi không liên quan đến tài liệu: "Tôi chỉ có thể trả lời các câu hỏi liên quan đến tài liệu được cung cấp."

        NGỮ CẢNH:
        {context}

        CÂU HỎI: {question}

        TRẢ LỜI:"""
    )
    
    return ChatPromptTemplate.from_template(template)