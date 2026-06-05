# JWT Secret Key Rotation Procedure

## Overview
JWT_SECRET_KEY is used to sign and verify authentication tokens. Each project must have a unique key.

## Current Status (2026-01-24)
- **agentic-commerce-arc**: Unique 256-bit key (rotated from placeholder)
- **trader-ai**: Unique 256-bit key
- **life-os-dashboard**: Uses Railway environment variables

## Rotation Procedure

### 1. Generate New Key
```bash
# PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))

# Or using OpenSSL
openssl rand -base64 32
```

### 2. Update Local Environment
```bash
# Edit .env file
JWT_SECRET_KEY=<new-key>
```

### 3. Update Production (Railway)
1. Go to Railway dashboard
2. Select the service
3. Navigate to Variables
4. Update JWT_SECRET_KEY
5. Redeploy

### 4. Invalidate Old Tokens
After rotation, all existing JWTs will become invalid. Users will need to re-authenticate.

## Rotation Schedule
- **Recommended**: Every 90 days
- **Required**: After any suspected compromise
- **On deployment**: For new environments

## Security Notes
- Never commit JWT secrets to git
- Use different keys for dev/staging/prod
- Minimum key length: 256 bits (32 bytes)
