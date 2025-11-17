import requests
import json
from typing import Optional
from models.user import User

class AIService:
    """Service for generating email content using AI (Ollama or OpenAI)"""
    
    @staticmethod
    async def generate_email(
        user: User,
        company_name: str,
        industry: str,
        description: str = "",
    ) -> dict:
        """
        Generate personalized email content using AI
        
        Args:
            user: User with AI settings
            company_name: Target company name
            industry: Industry/business type
            description: Company description
            
        Returns:
            Dict with subject and body
        """
        prompt = f"""Write a professional business email to {company_name}, a {industry} company.

Company Info: {description}

The email should:
1. Introduce {user.company_name or user.full_name}
2. Mention a relevant partnership opportunity
3. Keep it concise (3-4 sentences)
4. End with a call to action

Return ONLY in this JSON format:
{{
    "subject": "email subject here",
    "body": "email body here"
}}"""

        try:
            if user.ai_provider == "openai":
                return await AIService._generate_with_openai(user, prompt)
            else:  # ollama
                return await AIService._generate_with_ollama(user, prompt)
        except Exception as e:
            print(f"❌ AI Generation Error: {str(e)}")
            # Fallback to template
            return {
                "subject": f"Partnership Opportunity with {user.company_name or user.full_name}",
                "body": f"""Hi {company_name} team,

I came across your {industry} business and was impressed by what you do. I believe there's a great opportunity for us to collaborate.

{user.company_name or user.full_name} specializes in helping businesses like yours grow through strategic partnerships.

Would you be open to a brief call to explore this further?

Best regards,
{user.full_name}"""
            }
    
    @staticmethod
    async def _generate_with_ollama(user: User, prompt: str) -> dict:
        """Generate email using Ollama"""
        try:
            base_url = user.ollama_base_url or "http://localhost:11434"
            model = user.ollama_model or "llama2"
            
            print(f"🤖 Generating email with Ollama ({model})")
            
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse the response
            generated_text = data.get("response", "{}")
            
            # Try to extract JSON from response
            try:
                email_data = json.loads(generated_text)
                if "subject" in email_data and "body" in email_data:
                    return email_data
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing failed, try to extract manually
            lines = generated_text.split("\n")
            subject = ""
            body = ""
            for line in lines:
                if "subject" in line.lower() and ":" in line:
                    subject = line.split(":", 1)[1].strip().strip('"\'')
                elif "body" in line.lower() and ":" in line:
                    body = line.split(":", 1)[1].strip().strip('"\'')
            
            if subject and body:
                return {"subject": subject, "body": body}
            
            raise Exception("Failed to parse Ollama response")
            
        except Exception as e:
            print(f"❌ Ollama Error: {str(e)}")
            raise
    
    @staticmethod
    async def _generate_with_openai(user: User, prompt: str) -> dict:
        """Generate email using OpenAI"""
        if not user.openai_api_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            print(f"🤖 Generating email with OpenAI (GPT-3.5)")
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {user.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a professional email writer. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            email_data = json.loads(content)
            
            return email_data
            
        except Exception as e:
            print(f"❌ OpenAI Error: {str(e)}")
            raise
    
    @staticmethod
    async def chat_with_b2b_assistant(
        user: User,
        message: str,
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Chat with B2B business assistant for queries about B2B marketing, lead generation, and company information
        
        Args:
            user: User with AI settings
            message: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            AI response
        """
        system_prompt = """You are an expert B2B marketing assistant specializing in lead generation, business development, and company research. You help users with:

1. B2B Marketing Strategies
2. Lead Generation Techniques
3. Company Research and Analysis
4. Sales Outreach Best Practices
5. Business Partnership Opportunities
6. Industry Insights and Trends
7. Cold Email and Outreach Strategies
8. CRM and Lead Management

Always provide actionable, professional advice. Be concise but comprehensive. Focus on B2B contexts and business relationships.

If asked about specific companies, provide general insights about their industry, business model, and potential partnership opportunities.

Keep responses professional, helpful, and focused on business growth."""

        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Keep last 10 messages for context
        
        # Add current user message
        messages.append({"role": "user", "content": message})

        try:
            if user.ai_provider == "openai":
                return await AIService._chat_with_openai(user, messages)
            else:  # ollama
                return await AIService._chat_with_ollama(user, messages)
        except Exception as e:
            print(f"❌ Chat Error: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later or contact support if the issue persists."
    
    @staticmethod
    async def _chat_with_openai(user: User, messages: list) -> str:
        """Chat using OpenAI"""
        if not user.openai_api_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            print(f"🤖 Chatting with OpenAI")
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {user.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"❌ OpenAI Chat Error: {str(e)}")
            raise
    
    @staticmethod
    async def _chat_with_ollama(user: User, messages: list) -> str:
        """Chat using Ollama"""
        try:
            base_url = user.ollama_base_url or "http://localhost:11434"
            model = user.ollama_model or "llama2"
            
            print(f"🤖 Chatting with Ollama ({model})")
            
            # Convert chat format to Ollama format
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n\n"
            
            prompt += "Assistant: "
            
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 300
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("response", "I apologize, but I couldn't generate a response.")
            
        except Exception as e:
            print(f"❌ Ollama Chat Error: {str(e)}")
            raise
