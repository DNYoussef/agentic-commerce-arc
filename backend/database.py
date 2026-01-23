"""
Database Module - SQLite with WAL mode for high-performance persistence.

Adapted from library component: components/database/connection_pool
Uses aiosqlite for async operations with WAL mode enabled for
concurrent reads and improved write performance.

Features:
- WAL mode for concurrent access
- Connection pooling via context manager
- Async session factory
- Schema initialization
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional

import aiosqlite

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/app.db")
WAL_MODE = True
BUSY_TIMEOUT = 5000  # 5 seconds

# COM-002: Use per-request connections instead of global shared connection
# to ensure proper transaction isolation between concurrent requests
_db_initialized = False
_init_lock = asyncio.Lock()


async def init_db():
    """
    Initialize the database schema.

    COM-002: Creates tables and sets WAL mode on first run only.
    Subsequent connections will use per-request isolation.
    """
    global _db_initialized

    # Ensure data directory exists
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Initializing database at {DATABASE_PATH}")

    async with _init_lock:
        if not _db_initialized:
            # Create a temporary connection just for initialization
            conn = await aiosqlite.connect(
                DATABASE_PATH,
                timeout=BUSY_TIMEOUT / 1000,
            )
            try:
                # Enable WAL mode for better concurrency
                if WAL_MODE:
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    await conn.execute("PRAGMA cache_size=10000")
                    await conn.execute("PRAGMA temp_store=MEMORY")
                    logger.info("WAL mode enabled")

                # Enable foreign keys
                await conn.execute("PRAGMA foreign_keys=ON")

                # Create tables
                await _create_tables(conn)
                await conn.commit()

                _db_initialized = True
                logger.info("Database initialized successfully")
            finally:
                await conn.close()


async def _create_tables(conn: aiosqlite.Connection):
    """Create all database tables."""

    # Users table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            wallet_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)

    # Create index on email for faster lookups
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
    """)

    # Products table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            image_url TEXT,
            source TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create index on external_id for price comparisons
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_external_id ON products(external_id)
    """)

    # Chat sessions table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Chat messages table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    """)

    # Generated images table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS generated_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            image_url TEXT NOT NULL,
            style TEXT,
            aspect_ratio TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Price comparisons table (cache)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS price_comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            source TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            url TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """)

    # Create composite index for price lookups
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_price_comparisons_product
        ON price_comparisons(product_id, source)
    """)

    # Transactions table (blockchain)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tx_hash TEXT UNIQUE,
            tx_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            amount REAL,
            token_address TEXT,
            idempotency_key TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Ensure idempotency_key column exists for older databases
    try:
        await conn.execute("ALTER TABLE transactions ADD COLUMN idempotency_key TEXT")
    except aiosqlite.OperationalError:
        pass

    # Create unique index for idempotency keys
    await conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_transactions_idempotency_key
        ON transactions(idempotency_key)
        WHERE idempotency_key IS NOT NULL
    """)

    logger.info("Database tables created")


async def close_db():
    """
    Close/cleanup database resources.

    COM-002: With per-request connections, this is now a no-op for cleanup.
    Individual connections are closed after each request.
    """
    global _db_initialized
    _db_initialized = False
    logger.info("Database cleanup complete")


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    FastAPI dependency that yields a database connection.

    COM-002: Creates a new connection per request for proper transaction isolation.
    COM-003: Added rollback on exceptions before closing connection.
    """
    if not _db_initialized:
        await init_db()

    conn = await aiosqlite.connect(
        DATABASE_PATH,
        timeout=BUSY_TIMEOUT / 1000,
    )
    await conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    Async context manager for database access inside helper functions.

    COM-002: Creates a new connection per context for proper transaction isolation.
    COM-003: Added rollback on exceptions before closing connection.
    """
    if not _db_initialized:
        await init_db()

    conn = await aiosqlite.connect(
        DATABASE_PATH,
        timeout=BUSY_TIMEOUT / 1000,
    )
    await conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()


class DatabaseSession:
    """
    Helper class for database operations with automatic commit/rollback.

    COM-002: Each session now uses its own connection for proper isolation.

    Usage:
        async with DatabaseSession() as session:
            await session.execute("INSERT INTO users (email) VALUES (?)", (email,))
            user_id = session.lastrowid
    """

    def __init__(self):
        self.connection: Optional[aiosqlite.Connection] = None
        self.cursor: Optional[aiosqlite.Cursor] = None
        self.lastrowid: Optional[int] = None
        self._owns_connection: bool = False

    async def __aenter__(self):
        if not _db_initialized:
            await init_db()

        # COM-002: Create dedicated connection for this session
        self.connection = await aiosqlite.connect(
            DATABASE_PATH,
            timeout=BUSY_TIMEOUT / 1000,
        )
        await self.connection.execute("PRAGMA foreign_keys=ON")
        self._owns_connection = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback on error
            if self.connection:
                await self.connection.rollback()
            logger.error(f"Database error: {exc_val}")
        else:
            # Commit changes
            if self.connection:
                await self.connection.commit()

        # COM-002: Close the dedicated connection
        if self._owns_connection and self.connection:
            await self.connection.close()

        return False

    async def execute(self, sql: str, parameters: tuple = ()) -> aiosqlite.Cursor:
        """Execute a SQL statement."""
        self.cursor = await self.connection.execute(sql, parameters)
        self.lastrowid = self.cursor.lastrowid
        return self.cursor

    async def executemany(self, sql: str, parameters: list) -> aiosqlite.Cursor:
        """Execute a SQL statement with multiple parameter sets."""
        self.cursor = await self.connection.executemany(sql, parameters)
        return self.cursor

    async def fetchone(self):
        """Fetch one row from the last query."""
        if self.cursor:
            return await self.cursor.fetchone()
        return None

    async def fetchall(self):
        """Fetch all rows from the last query."""
        if self.cursor:
            return await self.cursor.fetchall()
        return []


# Convenience functions for common operations

async def get_user_by_email(email: str) -> Optional[dict]:
    """Get a user by email address."""
    async with get_db_context() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get a user by ID."""
    async with get_db_context() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def create_user(email: str, hashed_password: str, wallet_address: Optional[str] = None) -> int:
    """Create a new user and return the user ID."""
    async with DatabaseSession() as session:
        await session.execute(
            "INSERT INTO users (email, hashed_password, wallet_address) VALUES (?, ?, ?)",
            (email, hashed_password, wallet_address)
        )
        return session.lastrowid


async def save_chat_message(session_id: int, role: str, content: str, metadata: Optional[str] = None):
    """Save a chat message."""
    async with DatabaseSession() as session:
        await session.execute(
            "INSERT INTO chat_messages (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
            (session_id, role, content, metadata)
        )
        return session.lastrowid


async def get_chat_history(session_id: int, limit: int = 50) -> list:
    """Get chat history for a session."""
    async with get_db_context() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (session_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in reversed(rows)]


async def save_generated_image(
    user_id: str,  # Accepts string to support wallet addresses and numeric IDs
    prompt: str,
    image_url: str,
    style: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    model: Optional[str] = None
) -> int:
    """Save a generated image record. user_id can be numeric ID or wallet address."""
    async with DatabaseSession() as session:
        await session.execute(
            """
            INSERT INTO generated_images
            (user_id, prompt, image_url, style, aspect_ratio, model)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, prompt, image_url, style, aspect_ratio, model)
        )
        return session.lastrowid


async def get_transaction_by_hash(tx_hash: str) -> Optional[dict]:
    """Fetch a transaction by its hash."""
    async with get_db_context() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM transactions WHERE tx_hash = ?",
            (tx_hash,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_transaction_by_idempotency_key(idempotency_key: str) -> Optional[dict]:
    """Fetch a transaction by idempotency key."""
    async with get_db_context() as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM transactions WHERE idempotency_key = ?",
            (idempotency_key,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def create_transaction(
    user_id: int,
    tx_hash: str,
    tx_type: str,
    status: str,
    amount: Optional[float] = None,
    token_address: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    metadata: Optional[str] = None,
) -> int:
    """Create a new transaction record."""
    async with DatabaseSession() as session:
        await session.execute(
            """
            INSERT INTO transactions
            (user_id, tx_hash, tx_type, status, amount, token_address, idempotency_key, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, tx_hash, tx_type, status, amount, token_address, idempotency_key, metadata)
        )
        return session.lastrowid


async def update_transaction_status(
    tx_hash: str,
    status: str,
    confirmed_at: Optional[str] = None,
    metadata: Optional[str] = None,
):
    """Update transaction status and metadata."""
    async with DatabaseSession() as session:
        await session.execute(
            """
            UPDATE transactions
            SET status = ?, confirmed_at = COALESCE(?, confirmed_at), metadata = COALESCE(?, metadata)
            WHERE tx_hash = ?
            """,
            (status, confirmed_at, metadata, tx_hash)
        )
