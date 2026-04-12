"""
LLM Router — tries Groq first, falls back to Gemini automatically.

Usage (in main.py):
    from backend.llm_router import llm_service

    # Use exactly like you used gemini_service before
    result = await llm_service.generate_schema_with_validation(query)
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _build_service():
    """
    Try to instantiate GroqService. If GROQ_API_KEY is missing or invalid,
    fall back to GeminiService.
    """
    groq_key = os.getenv("GROQ_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if groq_key and groq_key not in ("your_groq_api_key_here", ""):
        try:
            from backend.groq_service import GroqService
            svc = GroqService()
            print("✅ LLM Router: Using GROQ as primary provider")
            return svc
        except Exception as e:
            print(f"⚠️  LLM Router: Groq init failed ({e}), trying Gemini...")

    # Fallback to Gemini
    if gemini_key and gemini_key not in ("your_gemini_api_key_here", ""):
        try:
            from backend.gemini_service import GeminiService
            svc = GeminiService()
            print("✅ LLM Router: Using GEMINI as fallback provider")
            return svc
        except Exception as e:
            raise RuntimeError(f"Both Groq and Gemini failed to initialize. Last error: {e}")

    raise RuntimeError(
        "No valid LLM API key found. "
        "Set GROQ_API_KEY (preferred) or GEMINI_API_KEY in your .env file."
    )


class LLMRouter:
    """
    Transparent wrapper that routes all calls through the active provider.
    On any 429/503/500 from Groq, it automatically retries on Gemini.
    """

    def __init__(self):
        self._primary = None
        self._fallback = None
        self._active_provider = None
        self._initialize()

    def _initialize(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        gemini_key = os.getenv("GEMINI_API_KEY", "")

        # Try Groq as primary
        if groq_key and groq_key not in ("your_groq_api_key_here", ""):
            try:
                from backend.groq_service import GroqService
                self._primary = GroqService()
                self._active_provider = "groq"
                print("✅ LLM Router: Primary = Groq")
            except Exception as e:
                print(f"⚠️  Groq init failed: {e}")

        # Try Gemini as fallback
        if gemini_key and gemini_key not in ("your_gemini_api_key_here", ""):
            try:
                from backend.gemini_service import GeminiService
                self._fallback = GeminiService()
                print("✅ LLM Router: Fallback = Gemini")
            except Exception as e:
                print(f"⚠️  Gemini init failed: {e}")

        if not self._primary and not self._fallback:
            raise RuntimeError(
                "No LLM provider could be initialized. "
                "Add GROQ_API_KEY or GEMINI_API_KEY to your .env file."
            )

        # If Groq failed but Gemini succeeded, use Gemini as primary
        if not self._primary and self._fallback:
            self._primary = self._fallback
            self._fallback = None
            self._active_provider = "gemini (only)"

    async def _call_with_fallback(self, method: str, *args, **kwargs):
        """
        Try method on primary provider. On any exception, retry on fallback.
        """
        providers = [p for p in [self._primary, self._fallback] if p is not None]
        last_error = None
        for provider in providers:
            try:
                fn = getattr(provider, method)
                result = await fn(*args, **kwargs)
                # If the result carries a Groq/Gemini quota error, try next provider
                if result.get("success") is False:
                    err = result.get("error", "")
                    if any(code in err for code in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE"]):
                        print(f"⚠️  Provider {type(provider).__name__} returned quota/availability error, switching...")
                        last_error = err
                        continue
                return result
            except Exception as e:
                last_error = str(e)
                print(f"⚠️  Provider {type(provider).__name__} raised: {e}, trying fallback...")
                continue

        return {"success": False, "error": f"All LLM providers failed. Last error: {last_error}"}

    def _call_sync_with_fallback(self, method: str, *args, **kwargs):
        providers = [p for p in [self._primary, self._fallback] if p is not None]
        last_error = None
        for provider in providers:
            try:
                fn = getattr(provider, method)
                result = fn(*args, **kwargs)
                return result
            except Exception as e:
                last_error = str(e)
                continue
        return {"success": False, "error": f"All LLM providers failed. Last error: {last_error}"}

    # ------------------------------------------------------------------
    # Public interface (same as GeminiService / GroqService)
    # ------------------------------------------------------------------

    async def generate_schema_with_validation(self, *args, **kwargs):
        return await self._call_with_fallback("generate_schema_with_validation", *args, **kwargs)

    async def generate_data(self, *args, **kwargs):
        return await self._call_with_fallback("generate_data", *args, **kwargs)

    async def generate_data_normal(self, *args, **kwargs):
        return await self._call_with_fallback("generate_data_normal", *args, **kwargs)

    async def generate_data_enhanced(self, *args, **kwargs):
        return await self._call_with_fallback("generate_data_enhanced", *args, **kwargs)

    async def compare_modes(self, *args, **kwargs):
        return await self._call_with_fallback("compare_modes", *args, **kwargs)

    def analyze_query(self, *args, **kwargs):
        return self._call_sync_with_fallback("analyze_query", *args, **kwargs)

    @property
    def provider(self) -> str:
        return self._active_provider or "unknown"


# Singleton — imported by main.py
llm_service = LLMRouter()
