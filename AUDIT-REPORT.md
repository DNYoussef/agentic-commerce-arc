# Security & Code Quality Audit Report

**Executive Summary**
- Completed a full source audit of `backend/`, `frontend/src/`, `contracts/src/`, and `lib/`.
- Found 2 high-severity issues (unauthenticated WebSocket access and funds-handling mismatch in purchase flow).
- Identified multiple medium/low issues in auth flow alignment, error handling, and test quality.
- Smart contract `SimpleEscrow` appears safe from common reentrancy/overflow issues given current design.

**Critical Findings (High Severity)**
- Unauthenticated WebSocket endpoint allows user impersonation and unauthorized access to chat streams; `user_id` is trusted from the URL and the `init` token is ignored in `backend/main.py:507` and `backend/main.py:544`.
- Purchase flow mixes ERC20 approval/USDC units with native ETH escrow calls, risking incorrect value transfer or user loss; `frontend/src/components/PurchaseModal.tsx:55` and `frontend/src/components/PurchaseModal.tsx:119`.

**Medium Findings**
- CORS allows credentials with wildcard origins, which is unsafe and can lead to credential leakage or misconfiguration across browsers; `backend/main.py:171`.
- `/auth/login` expects `application/x-www-form-urlencoded`, but frontend sends JSON; `/auth/refresh` expects a query parameter, but frontend sends JSON; `backend/main.py:221`, `backend/main.py:229`, `frontend/src/hooks/useAuth.ts:88`, `frontend/src/hooks/useAuth.ts:120`, `frontend/src/hooks/useAuth.ts:140`.
- Tool-call parsing uses `json.loads` without guarding against invalid JSON from LLM tool calls, causing 500s; `backend/agent.py:452`.
- Image-generation tool stores `user_id` as `int(user_id)` which fails for wallet-address WebSocket sessions; `backend/agent.py:297`.
- Database test config sets `DATABASE_URL`, but runtime uses `DATABASE_PATH`, causing tests to hit the real DB; `backend/database.py:27` and `backend/tests/conftest.py:10`.
- Tokens are stored in `localStorage`, increasing XSS exposure; `frontend/src/hooks/useAuth.ts:54`.

**Low Findings**
- `get_current_user_optional` likely never returns `None` when unauthenticated because `OAuth2PasswordBearer` raises before the dependency runs; `backend/auth.py:420`.
- Image generator expects `{ url }` but backend returns `{ image_url }`, so UI drops the result; `frontend/src/components/ImageGenerator.tsx:56`.
- Chat purchase flow uses a localStorage flag as approval state instead of rechecking allowance, which can break real transaction state; `frontend/src/components/ChatWindow.tsx:114`.
- Wallet button copies and links the **truncated** address instead of the full address; `frontend/src/components/WalletButton.tsx:100`.
- Theater tests: trivial or import-only tests that don’t validate app behavior (`backend/tests/test_smoke.py:1`, `backend/tests/test_spec_validation_import.py:1`, `backend/tests/test_quality_validator_import.py:1`).

**Recommendations**
1. Require WebSocket authentication and bind `user_id` to a verified JWT; reject connections without valid auth.
2. Align escrow flow with actual on-chain asset: either use ETH-only escrow (no ERC20 approval) or implement ERC20 escrow contract and UI accordingly.
3. Fix auth payload mismatch: use form-encoded login or update backend to accept JSON; update refresh to accept JSON body.
4. Harden tool-call parsing with safe JSON handling and structured validation before execution.
5. Standardize DB configuration: honor `DATABASE_URL` or update tests to use `DATABASE_PATH`.
6. Move access/refresh tokens to httpOnly cookies to reduce XSS exposure.
7. Replace or expand theater tests with behavior-based assertions and meaningful integration coverage.

**File-by-File Findings**
- `backend/main.py:171` – `allow_origins="*"` with `allow_credentials=True` is unsafe.
- `backend/main.py:221` – `/auth/login` expects form data but frontend sends JSON.
- `backend/main.py:229` – `/auth/refresh` expects query param but frontend sends JSON.
- `backend/main.py:507` – WebSocket accepts any `user_id` with no auth check.
- `backend/main.py:544` – `init` messages are ignored (token never validated).
- `backend/main.py:136` – Global singletons (`commerce_agent`, `ws_manager`) reduce testability and DI flexibility.

- `backend/agent.py:452` – Unhandled `json.loads` failure on tool args can crash requests.
- `backend/agent.py:297` – `int(user_id)` fails for wallet address sessions.

- `backend/auth.py:32` – `SECRET_KEY` defaults to random value if env missing, causing multi-worker token inconsistency.
- `backend/auth.py:420` – Optional auth dependency is ineffective with `OAuth2PasswordBearer` defaults.

- `backend/database.py:27` – `DATABASE_PATH` is used, ignoring `DATABASE_URL` used in tests.
- `backend/database.py:31` – Single global connection risks concurrency bottlenecks and tight coupling.

- `backend/tests/conftest.py:10` – Sets `DATABASE_URL` but backend ignores it.

- `backend/tests/test_smoke.py:1` – Empty smoke test (`assert True`) provides no coverage.
- `backend/tests/test_spec_validation_import.py:1` – Import-only test (theater).
- `backend/tests/test_quality_validator_import.py:1` – Import-only test (theater).

- `frontend/src/hooks/useAuth.ts:88` – JSON payload for `/auth/login` mismatches backend form requirement.
- `frontend/src/hooks/useAuth.ts:140` – JSON payload for `/auth/refresh` mismatches backend query param requirement.
- `frontend/src/hooks/useAuth.ts:54` – Tokens stored in `localStorage`.

- `frontend/src/components/PurchaseModal.tsx:55` – USDC units (`parseUnits(..., 6)`) used with ETH escrow.
- `frontend/src/components/PurchaseModal.tsx:119` – `value` sends native token despite ERC20 approval flow.

- `frontend/src/components/ChatWindow.tsx:114` – Approval state cached in `localStorage`, not confirmed on-chain.
- `frontend/src/components/ChatWindow.tsx:158` – `parseEther` assumes native token pricing, while backend prices are in USD.

- `frontend/src/components/ImageGenerator.tsx:56` – Expects `data.url` instead of `data.image_url`.

- `frontend/src/components/WalletButton.tsx:100` – Copies and links truncated address.

If you want, I can propose a patch plan or fix the highest-severity items first.