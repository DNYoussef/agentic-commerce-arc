"""
Commerce Agent - AI-powered shopping assistant with tool use.

This module implements the core AI agent for Agentic Commerce on Arc.
Uses OpenRouter for LLM access (Claude, GPT-4, etc.) with function calling to perform:
- Product search and recommendations
- Image generation via Replicate
- Price comparisons across sources
- Blockchain interactions

Architecture:
- Tool registry with typed parameters
- Streaming response support
- Context-aware conversation management

Updated 2026-01-12: Switched from Anthropic to OpenRouter for model flexibility.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from openai import AsyncOpenAI, APIError

from tools.replicate import ReplicateClient
from tools.price_compare import PriceComparer
from database import save_chat_message, get_chat_history, save_generated_image

logger = logging.getLogger(__name__)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass
class Tool:
    """Definition of an agent tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    requires_auth: bool = False


@dataclass
class AgentContext:
    """Context for agent conversations."""
    user_id: str
    session_id: Optional[int] = None
    wallet_address: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, str]] = field(default_factory=list)


class CommerceAgent:
    """
    AI-powered commerce agent using OpenRouter (Claude/GPT-4).

    Provides conversational shopping assistance with tool integration
    for product search, image generation, and price comparison.
    """

    SYSTEM_PROMPT = """You are an intelligent shopping assistant for Agentic Commerce on Arc.

Your capabilities:
1. PRODUCT SEARCH: Find products matching user criteria
2. IMAGE GENERATION: Create product visualizations using AI
3. PRICE COMPARISON: Compare prices across multiple sources
4. RECOMMENDATIONS: Suggest products based on preferences

Guidelines:
- Be helpful, concise, and accurate
- Always explain your actions and tool usage
- Ask clarifying questions when needed
- Respect user privacy and security
- For blockchain transactions, always confirm with the user first

When using tools:
- Use search_products for finding products
- Use generate_image for creating product images
- Use compare_prices for price comparisons

Format your responses clearly with sections when presenting multiple products or comparisons."""

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.replicate: Optional[ReplicateClient] = None
        self.price_comparer: Optional[PriceComparer] = None
        self.tools: List[Tool] = []
        self._initialized = False

    async def initialize(self):
        """Initialize the agent and its tools."""
        if self._initialized:
            return

        logger.info("Initializing Commerce Agent...")

        # Initialize OpenRouter client (OpenAI-compatible API)
        if OPENROUTER_API_KEY:
            self.client = AsyncOpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url=OPENROUTER_BASE_URL,
                default_headers={
                    "HTTP-Referer": "https://agentic-commerce-arc.railway.app",
                    "X-Title": "Agentic Commerce on Arc"
                }
            )
            logger.info(f"OpenRouter client initialized with model: {MODEL_NAME}")
        else:
            logger.warning("OPENROUTER_API_KEY not set - agent will use mock responses")

        # Initialize tool clients
        self.replicate = ReplicateClient()
        await self.replicate.initialize()

        self.price_comparer = PriceComparer()

        # Register tools
        self._register_tools()

        self._initialized = True
        logger.info("Commerce Agent initialized successfully")

    def _register_tools(self):
        """Register available tools."""
        self.tools = [
            Tool(
                name="search_products",
                description="Search for products matching the given criteria",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for products"
                        },
                        "category": {
                            "type": "string",
                            "description": "Product category filter (optional)"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price filter (optional)"
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price filter (optional)"
                        }
                    },
                    "required": ["query"]
                },
                handler=self._handle_search_products
            ),
            Tool(
                name="generate_image",
                description="Generate a product image based on a text description",
                parameters={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Detailed description of the image to generate"
                        },
                        "style": {
                            "type": "string",
                            "enum": ["product", "lifestyle", "minimalist", "artistic"],
                            "description": "Style of the generated image"
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["1:1", "16:9", "4:3", "3:4"],
                            "description": "Aspect ratio for the image"
                        }
                    },
                    "required": ["prompt"]
                },
                handler=self._handle_generate_image
            ),
            Tool(
                name="compare_prices",
                description="Compare prices for a product across multiple sources",
                parameters={
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "Name of the product to compare"
                        },
                        "product_id": {
                            "type": "string",
                            "description": "Product ID if known (optional)"
                        }
                    },
                    "required": ["product_name"]
                },
                handler=self._handle_compare_prices
            ),
        ]

    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get tools in Anthropic API format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters
            }
            for tool in self.tools
        ]

    async def _handle_search_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Handle product search tool."""
        # For now, return mock data
        # In production, integrate with actual product APIs
        logger.info(f"Searching products: query={query}, category={category}")

        # Mock product results
        products = [
            {
                "id": "prod_001",
                "name": f"Premium {query.title()}",
                "description": f"High-quality {query} with excellent features",
                "price": 99.99,
                "currency": "USD",
                "category": category or "general",
                "image_url": "https://via.placeholder.com/300",
                "source": "agentic-commerce",
                "rating": 4.5,
            },
            {
                "id": "prod_002",
                "name": f"Budget {query.title()}",
                "description": f"Affordable {query} with good value",
                "price": 49.99,
                "currency": "USD",
                "category": category or "general",
                "image_url": "https://via.placeholder.com/300",
                "source": "agentic-commerce",
                "rating": 4.0,
            },
            {
                "id": "prod_003",
                "name": f"Luxury {query.title()}",
                "description": f"Premium {query} with top-tier quality",
                "price": 199.99,
                "currency": "USD",
                "category": category or "general",
                "image_url": "https://via.placeholder.com/300",
                "source": "agentic-commerce",
                "rating": 4.8,
            },
        ]

        # Apply price filters
        if min_price is not None:
            products = [p for p in products if p["price"] >= min_price]
        if max_price is not None:
            products = [p for p in products if p["price"] <= max_price]

        return products

    async def _handle_generate_image(
        self,
        prompt: str,
        style: str = "product",
        aspect_ratio: str = "1:1",
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle image generation tool."""
        logger.info(f"Generating image: prompt={prompt[:50]}..., style={style}")

        if self.replicate:
            result = await self.replicate.generate_image(
                prompt=prompt,
                style=style,
                aspect_ratio=aspect_ratio
            )

            # Save to database if user_id provided
            if user_id and result.get("image_url"):
                await save_generated_image(
                    user_id=int(user_id),
                    prompt=prompt,
                    image_url=result["image_url"],
                    style=style,
                    aspect_ratio=aspect_ratio,
                    model=result.get("model")
                )

            return result
        else:
            # Mock response if Replicate not configured
            return {
                "image_url": "https://via.placeholder.com/512",
                "prompt": prompt,
                "style": style,
                "model": "mock"
            }

    async def _handle_compare_prices(
        self,
        product_name: str,
        product_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle price comparison tool."""
        logger.info(f"Comparing prices: product={product_name}")

        if self.price_comparer:
            return await self.price_comparer.compare(
                product_name=product_name,
                product_id=product_id
            )
        else:
            # Mock response
            return {
                "product_name": product_name,
                "sources": [
                    {"source": "Amazon", "price": 99.99, "url": "https://amazon.com"},
                    {"source": "eBay", "price": 89.99, "url": "https://ebay.com"},
                    {"source": "Walmart", "price": 94.99, "url": "https://walmart.com"},
                ],
                "best_deal": {"source": "eBay", "price": 89.99, "savings": 10.00}
            }

    async def _execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        context: Optional[AgentContext] = None
    ) -> Any:
        """Execute a tool by name."""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Add context info to tool input
        if context:
            tool_input["user_id"] = context.user_id

        return await tool.handler(**tool_input)

    async def process_message(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return the agent response.

        Args:
            message: User's message
            user_id: User ID for context
            context: Additional context data
            session_id: Chat session ID for history

        Returns:
            Response with message, actions, products, and images
        """
        agent_context = AgentContext(
            user_id=user_id,
            session_id=session_id,
            preferences=context or {}
        )

        # Get chat history if session exists
        if session_id:
            history = await get_chat_history(session_id, limit=10)
            agent_context.history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ]

        # Build messages
        messages = agent_context.history + [{"role": "user", "content": message}]

        # Call LLM via OpenRouter
        if self.client:
            response = await self._call_llm(messages, agent_context)
        else:
            # Mock response
            response = {
                "message": f"I received your message about: {message[:100]}... However, the AI service is not configured. Please set up OPENROUTER_API_KEY.",
                "actions": [],
                "products": [],
                "images": []
            }

        # Save messages to database
        if session_id:
            await save_chat_message(session_id, "user", message)
            await save_chat_message(session_id, "assistant", response["message"])

        return response

    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        context: AgentContext
    ) -> Dict[str, Any]:
        """Call OpenRouter API with tools."""
        try:
            # Convert tools to OpenAI function format
            tools_schema = self._get_openai_tools_schema()

            # Build messages with system prompt
            full_messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + messages

            response = await self.client.chat.completions.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                messages=full_messages,
                tools=tools_schema if tools_schema else None
            )

            # Process response
            result = {
                "message": "",
                "actions": [],
                "products": [],
                "images": []
            }

            # Handle response content
            choice = response.choices[0]
            if choice.message.content:
                result["message"] = choice.message.content

            # Handle tool calls (OpenAI format)
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute tool
                    tool_result = await self._execute_tool(
                        tool_name,
                        tool_args,
                        context
                    )

                    # Add to appropriate result list
                    if tool_name == "search_products":
                        result["products"] = tool_result
                        result["actions"].append({
                            "type": "search",
                            "query": tool_args.get("query")
                        })
                    elif tool_name == "generate_image":
                        result["images"].append(tool_result)
                        result["actions"].append({
                            "type": "generate_image",
                            "prompt": tool_args.get("prompt")
                        })
                    elif tool_name == "compare_prices":
                        result["message"] += f"\n\nPrice Comparison:\n{json.dumps(tool_result, indent=2)}"
                        result["actions"].append({
                            "type": "compare_prices",
                            "product": tool_args.get("product_name")
                        })

            return result

        except APIError as e:
            logger.error(f"OpenRouter API error: {e}")
            return {
                "message": "I encountered an error processing your request. Please try again.",
                "actions": [],
                "products": [],
                "images": []
            }

    def _get_openai_tools_schema(self) -> List[Dict[str, Any]]:
        """Convert tools to OpenAI function calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools
        ]

    async def stream_response(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a response for real-time chat.

        Yields chunks as they're generated.
        """
        agent_context = AgentContext(
            user_id=user_id,
            preferences=context or {}
        )

        if not self.client:
            async for chunk in self._stream_mock_response(message):
                yield chunk
            return

        async for chunk in self._stream_openrouter(message, agent_context):
            yield chunk

    async def _stream_mock_response(
        self,
        message: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield a mock streaming response."""
        mock_response = f"Processing your request: {message[:50]}..."
        for i in range(0, len(mock_response), 10):
            yield {
                "content": mock_response[i:i + 10],
                "metadata": {"type": "text"}
            }
            await asyncio.sleep(0.1)

    async def _stream_openrouter(
        self,
        message: str,
        context: AgentContext
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream OpenRouter response with tool execution."""
        messages = [{"role": "user", "content": message}]
        tool_calls: Dict[str, Dict[str, str]] = {}

        try:
            stream = await self.client.chat.completions.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "system", "content": self.SYSTEM_PROMPT}] + messages,
                tools=self._get_openai_tools_schema() or None,
                stream=True
            )

            async for chunk in stream:
                if not chunk.choices or not chunk.choices[0].delta:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    yield {
                        "content": delta.content,
                        "metadata": {"type": "text"}
                    }
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        await self._accumulate_tool_call(tool_calls, tool_call)
                        if tool_call.function and tool_call.function.name:
                            yield {
                                "content": "",
                                "metadata": {
                                    "type": "tool_start",
                                    "tool": tool_call.function.name,
                                }
                            }

            async for result in self._emit_tool_results(tool_calls, context):
                yield result

        except APIError as e:
            logger.error(f"Streaming error: {e}")
            yield {
                "content": "An error occurred while processing your request.",
                "metadata": {"type": "error", "error": str(e)}
            }

    async def _accumulate_tool_call(
        self,
        tool_calls: Dict[str, Dict[str, str]],
        tool_call: Any
    ) -> None:
        """Collect tool call arguments from streaming deltas."""
        call_id = tool_call.id or f"call_{len(tool_calls)}"
        if call_id not in tool_calls:
            tool_calls[call_id] = {"name": "", "args": ""}

        if tool_call.function and tool_call.function.name:
            tool_calls[call_id]["name"] = tool_call.function.name
        if tool_call.function and tool_call.function.arguments:
            tool_calls[call_id]["args"] += tool_call.function.arguments

    async def _emit_tool_results(
        self,
        tool_calls: Dict[str, Dict[str, str]],
        context: AgentContext
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute tool calls and yield results."""
        for call in tool_calls.values():
            tool_name = call.get("name")
            if not tool_name:
                continue
            tool_args = self._safe_json_load(call.get("args", ""))
            try:
                result = await self._execute_tool(tool_name, tool_args, context)
            except Exception as exc:
                logger.error("Tool execution failed: %s", exc)
                result = {"error": str(exc)}

            metadata = {
                "type": "tool_result",
                "tool": tool_name,
                "result": result,
            }
            if tool_name == "search_products":
                metadata["products"] = result
            if tool_name == "generate_image":
                metadata["image"] = result
            if tool_name == "compare_prices":
                metadata["comparison"] = result

            yield {"content": "", "metadata": metadata}

    @staticmethod
    def _safe_json_load(raw: str) -> Dict[str, Any]:
        """Safely parse tool arguments from JSON."""
        try:
            return json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return {}

    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Direct product search (bypasses LLM)."""
        return await self._handle_search_products(
            query=query,
            category=category,
            max_price=max_price,
            min_price=min_price
        )

    async def compare_prices(self, product_id: str) -> Dict[str, Any]:
        """Direct price comparison (bypasses LLM)."""
        return await self._handle_compare_prices(
            product_name=product_id,  # Will be looked up
            product_id=product_id
        )

    async def generate_product_image(
        self,
        prompt: str,
        style: str = "product",
        aspect_ratio: str = "1:1"
    ) -> Dict[str, Any]:
        """Direct image generation (bypasses LLM)."""
        return await self._handle_generate_image(
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio
        )

    async def shutdown(self):
        """Clean shutdown of agent resources."""
        logger.info("Shutting down Commerce Agent...")

        if self.replicate:
            await self.replicate.shutdown()

        self._initialized = False
        logger.info("Commerce Agent shutdown complete")
