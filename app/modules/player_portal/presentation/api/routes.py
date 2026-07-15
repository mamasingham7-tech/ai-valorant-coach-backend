import structlog
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from app.shared.responses.envelope import wrap_response, APIResponseEnvelope
from app.modules.player_portal.application.schemas import (
    RiotIDLinkRequest, RiotAccountResponse, RankResponse,
    MatchSummaryResponse, SyncStatusResponse, PlayerStatsResponse,
)
from app.modules.player_portal.application.services.provider_factory import get_valorant_provider
from app.modules.player_portal.application.services.sync_service import SyncService

logger = structlog.get_logger()
router = APIRouter(prefix="/portal", tags=["Player Portal & Riot Account"])

def get_sync_service() -> SyncService:
    """FastAPI dependency: injects the active SyncService with the configured provider."""
    return SyncService(provider=get_valorant_provider())

def _rid(request: Request) -> str:
    return getattr(request.state, "request_id", "n/a")

# ─────────────────────────────────────────────────────────────────────────────
# Provider info (public)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/provider", response_model=APIResponseEnvelope)
async def get_provider_info(request: Request):
    """Returns which Valorant data provider is currently active and why."""
    provider = get_valorant_provider()
    info = {
        "provider": provider.provider_name,
        "henrikdev": "Primary provider. Community API. No API key required for free tier.",
        "riot_official": "Secondary provider. Requires approved RIOT_API_KEY from developer.riotgames.com.",
        "mock": "Development provider. Returns realistic fake data. No external calls.",
        "note": "Riot RSO (Sign-in with Riot OAuth) is NOT publicly available. It is exclusive to Riot official partners only.",
        "docs": {
            "henrikdev": "https://docs.henrikdev.xyz/valorant/general",
            "riot_official": "https://developer.riotgames.com/apis",
        }
    }
    return wrap_response(success=True, data=info, message="Provider info", request_id=_rid(request))

# ─────────────────────────────────────────────────────────────────────────────
# Account lookup / linking (public — no auth required)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/verify-riot-id", response_model=APIResponseEnvelope)
async def verify_riot_id(
    request: Request,
    body: RiotIDLinkRequest,
    sync_service: SyncService = Depends(get_sync_service),
):
    """Publicly verify that a Riot ID exists and return basic account info.
    Used during the registration / account linking flow — no authentication required.
    """
    game_name, tag_line = body.riot_id.split("#", 1)
    account = await sync_service.link_account("anonymous", game_name, tag_line)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Riot account '{body.riot_id}' not found. Check your Riot ID and try again."
        )
    return wrap_response(
        success=True,
        data={
            "verified": True,
            "game_name": account.game_name,
            "tag_line": account.tag_line,
            "riot_id": account.riot_id,
            "region": account.region,
            "account_level": account.account_level,
            "provider": account.provider,
        },
        message=f"Riot ID '{account.riot_id}' verified successfully",
        request_id=_rid(request)
    )

# ─────────────────────────────────────────────────────────────────────────────
# Rank
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/rank", response_model=APIResponseEnvelope)
async def get_rank(
    request: Request,
    riot_id: str = Query(..., description="Riot ID in format Name#Tag"),
    region: str = Query("na", description="Region: na, eu, ap, kr, latam, br"),
    sync_service: SyncService = Depends(get_sync_service),
):
    """Fetch the current competitive rank, RR, and peak rank for a Riot ID."""
    if "#" not in riot_id:
        raise HTTPException(status_code=400, detail="riot_id must be in format Name#Tag")
    game_name, tag_line = riot_id.split("#", 1)
    rank = await sync_service.get_rank(game_name, tag_line, region)
    return wrap_response(
        success=True,
        data=rank,
        message="Rank data fetched" if rank else "Rank data unavailable",
        request_id=_rid(request)
    )

# ─────────────────────────────────────────────────────────────────────────────
# Match history
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/matches", response_model=APIResponseEnvelope)
async def get_matches(
    request: Request,
    riot_id: str = Query(..., description="Riot ID in format Name#Tag"),
    region: str = Query("na", description="Region: na, eu, ap, kr, latam, br"),
    mode: str = Query("competitive", description="Game mode: competitive, unrated, swiftplay, deathmatch"),
    size: int = Query(20, ge=1, le=50, description="Number of matches to return (max 50)"),
    sync_service: SyncService = Depends(get_sync_service),
):
    """Fetch match history for a Riot ID with optional mode and size filters."""
    if "#" not in riot_id:
        raise HTTPException(status_code=400, detail="riot_id must be in format Name#Tag")
    game_name, tag_line = riot_id.split("#", 1)
    matches = await sync_service.get_matches(game_name, tag_line, region, mode, size)
    return wrap_response(
        success=True,
        data={"matches": matches, "count": len(matches), "mode": mode},
        message=f"Match history fetched — {len(matches)} matches",
        request_id=_rid(request)
    )

# ─────────────────────────────────────────────────────────────────────────────
# Full player stats (account + rank + matches in one call)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/player-stats", response_model=APIResponseEnvelope)
async def get_player_stats(
    request: Request,
    riot_id: str = Query(..., description="Riot ID in format Name#Tag"),
    region: str = Query("na"),
    sync_service: SyncService = Depends(get_sync_service),
):
    """Fetch combined account + rank + match history in a single call.
    This is the primary endpoint used by the frontend dashboard.
    """
    if "#" not in riot_id:
        raise HTTPException(status_code=400, detail="riot_id must be in format Name#Tag")
    game_name, tag_line = riot_id.split("#", 1)

    # Parallel-friendly: each call checks cache independently
    account = await sync_service.link_account("public", game_name, tag_line)
    if not account:
        raise HTTPException(status_code=404, detail=f"Riot account '{riot_id}' not found")

    rank    = await sync_service.get_rank(game_name, tag_line, region)
    matches = await sync_service.get_matches(game_name, tag_line, region, "competitive", 20)

    # Calculate aggregate stats
    win_rate = avg_acs = avg_hs = avg_kda = None
    if matches:
        wins     = sum(1 for m in matches if m.get("result") == "WIN")
        win_rate = round(wins / len(matches) * 100, 1)
        avg_acs  = round(sum(m.get("acs", 0) for m in matches) / len(matches), 1)
        avg_hs   = round(sum(m.get("hs_percent", 0) for m in matches) / len(matches), 1)
        kda_vals = [(m.get("kills", 0) + m.get("assists", 0)) / max(m.get("deaths", 1), 1) for m in matches]
        avg_kda  = round(sum(kda_vals) / len(kda_vals), 2)

    return wrap_response(
        success=True,
        data={
            "riot_id": riot_id,
            "game_name": account.game_name,
            "tag_line": account.tag_line,
            "region": account.region,
            "account_level": account.account_level,
            "provider": account.provider,
            "rank": rank,
            "recent_matches": matches,
            "stats": {
                "win_rate": win_rate,
                "avg_acs": avg_acs,
                "avg_hs_percent": avg_hs,
                "avg_kda": avg_kda,
                "matches_analyzed": len(matches),
            }
        },
        message=f"Full stats for {riot_id}",
        request_id=_rid(request)
    )

# ─────────────────────────────────────────────────────────────────────────────
# Sync status
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/sync-status", response_model=APIResponseEnvelope)
async def sync_status(request: Request):
    """Returns current provider configuration and sync status."""
    provider = get_valorant_provider()
    return wrap_response(
        success=True,
        data=SyncStatusResponse(
            provider=provider.provider_name,
            account_linked=False,
        ),
        message="Sync status",
        request_id=_rid(request)
    )
