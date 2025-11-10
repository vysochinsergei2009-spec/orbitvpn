"""FastAPI Web Dashboard Application"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manager.config.manager_config import ManagerConfig, load_config
from manager.core.supervisor import ServiceSupervisor
from manager.services.telegram_bot import TelegramBotService
from manager.services.marzban import MarzbanMonitorService
from manager.services.redis import RedisMonitorService
from manager.services.postgres import PostgresMonitorService
from manager.utils.logger import setup_logging, get_logger

LOG = get_logger(__name__)

# Global supervisor instance
_supervisor: Optional[ServiceSupervisor] = None
_config: Optional[ManagerConfig] = None


def get_supervisor() -> ServiceSupervisor:
    """Get or create supervisor instance."""
    global _supervisor, _config

    if _supervisor is None:
        _config = load_config()
        _supervisor = ServiceSupervisor(_config)

        # Register services
        if _config.telegram_bot.enabled:
            _supervisor.register_service(TelegramBotService(_config.telegram_bot))
        if _config.marzban_monitor.enabled:
            _supervisor.register_service(MarzbanMonitorService(_config.marzban_monitor))
        if _config.redis.enabled:
            _supervisor.register_service(RedisMonitorService(_config.redis))
        if _config.postgres.enabled:
            _supervisor.register_service(PostgresMonitorService(_config.postgres))

    return _supervisor


def get_config() -> ManagerConfig:
    """Get configuration."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def hash_password(password: str) -> str:
    """Hash password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed


async def get_current_user(request: Request) -> str:
    """Get current authenticated user."""
    config = get_config()

    if not config.web_dashboard.auth_enabled:
        return "admin"  # No auth required

    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return username


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    config = get_config()

    # Setup logging
    setup_logging(
        log_level=config.logging.level,
        log_file=config.project_dir / "logs" / "dashboard.log"
    )

    app = FastAPI(
        title="OrbitVPN Service Manager",
        description="Web dashboard for managing OrbitVPN services",
        version="1.0.0"
    )

    # Add middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.web_dashboard.secret_key or secrets.token_hex(32)
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup templates and static files
    templates_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"

    templates_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)

    templates = Jinja2Templates(directory=str(templates_dir))

    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Routes
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request, username: str = Depends(get_current_user)):
        """Main dashboard page."""
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "username": username}
        )

    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        """Login page."""
        config = get_config()
        if not config.web_dashboard.auth_enabled:
            return HTMLResponse(
                '<script>window.location.href="/";</script>'
            )

        return templates.TemplateResponse("login.html", {"request": request})

    @app.post("/api/login")
    async def login(request: Request):
        """Handle login."""
        config = get_config()

        if not config.web_dashboard.auth_enabled:
            return {"success": True}

        data = await request.json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Missing credentials")

        # Check credentials
        stored_hash = config.web_dashboard.admin_users.get(username)
        if not stored_hash or not verify_password(password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Set session
        request.session["username"] = username
        return {"success": True}

    @app.post("/api/logout")
    async def logout(request: Request):
        """Handle logout."""
        request.session.clear()
        return {"success": True}

    @app.get("/api/status")
    async def get_status(username: str = Depends(get_current_user)):
        """Get system status."""
        supervisor = get_supervisor()
        status = await supervisor.get_system_status()
        return status

    @app.get("/api/services")
    async def get_services(username: str = Depends(get_current_user)):
        """Get all services information."""
        supervisor = get_supervisor()
        services_info = await supervisor.get_all_services_info()

        return {
            "services": {
                name: info.to_dict()
                for name, info in services_info.items()
            }
        }

    @app.post("/api/services/{service_name}/start")
    async def start_service(service_name: str, username: str = Depends(get_current_user)):
        """Start a service."""
        supervisor = get_supervisor()
        success = await supervisor.start_service(service_name)

        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to start {service_name}")

        return {"success": True, "service": service_name, "action": "start"}

    @app.post("/api/services/{service_name}/stop")
    async def stop_service(service_name: str, username: str = Depends(get_current_user)):
        """Stop a service."""
        supervisor = get_supervisor()
        success = await supervisor.stop_service(service_name)

        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to stop {service_name}")

        return {"success": True, "service": service_name, "action": "stop"}

    @app.post("/api/services/{service_name}/restart")
    async def restart_service(service_name: str, username: str = Depends(get_current_user)):
        """Restart a service."""
        supervisor = get_supervisor()
        success = await supervisor.restart_service(service_name)

        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to restart {service_name}")

        return {"success": True, "service": service_name, "action": "restart"}

    @app.get("/api/marzban/instances")
    async def get_marzban_instances(username: str = Depends(get_current_user)):
        """Get Marzban instances information."""
        supervisor = get_supervisor()

        # Find Marzban service
        marzban_service = None
        for service in supervisor._services.values():
            if isinstance(service, MarzbanMonitorService):
                marzban_service = service
                break

        if not marzban_service:
            return {"instances": []}

        instances = await marzban_service.get_instances_info()
        return {
            "instances": [inst.to_dict() for inst in instances]
        }

    @app.get("/api/marzban/instances/{instance_id}")
    async def get_marzban_instance(instance_id: str, username: str = Depends(get_current_user)):
        """Get specific Marzban instance details."""
        supervisor = get_supervisor()

        marzban_service = None
        for service in supervisor._services.values():
            if isinstance(service, MarzbanMonitorService):
                marzban_service = service
                break

        if not marzban_service:
            raise HTTPException(status_code=404, detail="Marzban service not found")

        instance = await marzban_service.get_instance_details(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        return instance.to_dict()

    @app.get("/api/metrics/history")
    async def get_metrics_history(
        service: Optional[str] = None,
        hours: int = 1,
        username: str = Depends(get_current_user)
    ):
        """Get metrics history."""
        supervisor = get_supervisor()
        collector = supervisor.get_metrics_collector()

        if service:
            history = collector.get_metrics_history(service, hours)
            return {
                "service": service,
                "metrics": [m.to_dict() for m in history]
            }
        else:
            all_metrics = collector.get_all_latest_metrics()
            return {
                "services": {
                    name: metrics.to_dict()
                    for name, metrics in all_metrics.items()
                }
            }

    @app.get("/api/users/stats")
    async def get_user_stats(username: str = Depends(get_current_user)):
        """Get user statistics."""
        from app.repo.db import get_db
        from app.repo.models import User, Config
        from sqlalchemy import select, func
        from datetime import datetime, timedelta

        async for db in get_db():
            # Total users
            total_users = await db.scalar(select(func.count(User.tg_id)))

            # Active subscriptions
            now = datetime.now()
            active_subs = await db.scalar(
                select(func.count(User.tg_id)).where(User.sub_end > now)
            )

            # Trial users
            trial_users = await db.scalar(
                select(func.count(User.tg_id)).where(
                    User.sub_end > now,
                    User.balance == 0
                )
            )

            # New today
            today_start = datetime.now().replace(hour=0, minute=0, second=0)
            new_today = await db.scalar(
                select(func.count(User.tg_id)).where(User.created_at >= today_start)
            )

            # Total configs
            total_configs = await db.scalar(select(func.count(Config.id)))

            return {
                "total_users": total_users or 0,
                "active_subscriptions": active_subs or 0,
                "trial_users": trial_users or 0,
                "new_today": new_today or 0,
                "total_configs": total_configs or 0
            }

    @app.websocket("/ws/logs/{service_name}")
    async def websocket_logs(websocket: WebSocket, service_name: str):
        """WebSocket endpoint for real-time logs."""
        await websocket.accept()

        try:
            supervisor = get_supervisor()

            # Get service
            if service_name not in supervisor._services:
                await websocket.send_json({"error": f"Service {service_name} not found"})
                await websocket.close()
                return

            service = supervisor._services[service_name]

            # Stream logs if it's telegram bot
            if isinstance(service, TelegramBotService):
                while True:
                    logs = await service.get_logs(lines=20)
                    await websocket.send_json({"logs": logs})
                    await asyncio.sleep(2)

        except WebSocketDisconnect:
            LOG.info(f"WebSocket disconnected for {service_name} logs")
        except Exception as e:
            LOG.error(f"WebSocket error: {e}")
            await websocket.close()

    @app.on_event("startup")
    async def startup():
        """Startup event."""
        LOG.info("Starting web dashboard...")
        supervisor = get_supervisor()
        await supervisor.start_monitoring()

    @app.on_event("shutdown")
    async def shutdown():
        """Shutdown event."""
        LOG.info("Shutting down web dashboard...")
        supervisor = get_supervisor()
        await supervisor.stop_monitoring()

    return app
