"""Telegram Bot Service Manager"""
import asyncio
import time
import signal
from pathlib import Path
from typing import Optional
from datetime import datetime

from manager.core.service import ManagedService
from manager.core.models import (
    ServiceStatus,
    HealthStatus,
    HealthCheckResult,
    ServiceMetrics
)
from manager.config.manager_config import TelegramBotConfig
from manager.utils.logger import get_logger

LOG = get_logger(__name__)


class TelegramBotService(ManagedService):
    """Manages the Telegram bot process"""

    def __init__(self, config: TelegramBotConfig):
        super().__init__("telegram_bot")
        self.config = config
        self._process: Optional[asyncio.subprocess.Process] = None
        self._start_time: Optional[datetime] = None

    async def start(self) -> bool:
        """Start the Telegram bot in a subprocess."""
        if self._status == ServiceStatus.RUNNING:
            LOG.warning("Bot is already running")
            return False

        try:
            self._set_status(ServiceStatus.STARTING)

            # Check if tmux session already exists
            check_cmd = f"tmux has-session -t {self.config.tmux_session} 2>/dev/null"
            result = await asyncio.create_subprocess_shell(
                check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                LOG.warning(f"Tmux session {self.config.tmux_session} already exists")
                # Get PID from tmux
                self._pid = await self._get_tmux_pid()
                self._set_started(self._pid)
                self._start_time = datetime.now()
                return True

            # Start bot in tmux session
            venv_path = Path("/root/orbitvpn/venv")
            run_script = Path("/root/orbitvpn/run.py")
            log_file = Path("/root/orbitvpn") / self.config.log_file

            start_cmd = (
                f"tmux new-session -d -s {self.config.tmux_session} "
                f"-c /root/orbitvpn "
                f"\"source {venv_path}/bin/activate && "
                f"python3 {run_script} 2>&1 | tee -a {log_file}\""
            )

            LOG.info(f"Starting bot with command: {start_cmd}")

            process = await asyncio.create_subprocess_shell(
                start_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await process.wait()

            if process.returncode == 0:
                # Give bot time to start
                await asyncio.sleep(2)

                # Get PID
                self._pid = await self._get_tmux_pid()

                if self._pid:
                    self._set_started(self._pid)
                    self._start_time = datetime.now()
                    LOG.info(f"Bot started successfully with PID {self._pid}")
                    return True
                else:
                    LOG.error("Bot process not found after start")
                    self._set_status(ServiceStatus.FAILED)
                    return False
            else:
                stderr = await process.stderr.read()
                LOG.error(f"Failed to start bot: {stderr.decode()}")
                self._set_status(ServiceStatus.FAILED)
                return False

        except Exception as e:
            LOG.error(f"Error starting bot: {e}")
            self._set_status(ServiceStatus.FAILED)
            return False

    async def stop(self, graceful: bool = True, timeout: int = 30) -> bool:
        """Stop the Telegram bot."""
        if self._status == ServiceStatus.STOPPED:
            LOG.warning("Bot is already stopped")
            return True

        try:
            self._set_status(ServiceStatus.STOPPING)

            # Check if session exists
            check_cmd = f"tmux has-session -t {self.config.tmux_session} 2>/dev/null"
            result = await asyncio.create_subprocess_shell(
                check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode != 0:
                LOG.info("Tmux session not found, bot already stopped")
                self._set_stopped()
                return True

            if graceful:
                # Send Ctrl+C for graceful shutdown
                stop_cmd = f"tmux send-keys -t {self.config.tmux_session} C-c"
                process = await asyncio.create_subprocess_shell(
                    stop_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.wait()

                # Wait for graceful shutdown
                await asyncio.sleep(2)

                # Check if still running
                check_result = await asyncio.create_subprocess_shell(
                    check_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await check_result.wait()

                if check_result.returncode != 0:
                    # Successfully stopped
                    self._set_stopped()
                    LOG.info("Bot stopped gracefully")
                    return True

            # Force kill if graceful failed or not requested
            kill_cmd = f"tmux kill-session -t {self.config.tmux_session}"
            process = await asyncio.create_subprocess_shell(
                kill_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()

            self._set_stopped()
            LOG.info("Bot stopped (forced)")
            return True

        except Exception as e:
            LOG.error(f"Error stopping bot: {e}")
            return False

    async def restart(self) -> bool:
        """Restart the bot."""
        self._set_status(ServiceStatus.RESTARTING)

        success = await self.stop(graceful=True, timeout=10)
        if not success:
            LOG.warning("Failed to stop bot, attempting to start anyway")

        await asyncio.sleep(2)
        success = await self.start()

        if success:
            self._increment_restart_count()

        return success

    async def health_check(self) -> HealthCheckResult:
        """Check if bot is healthy."""
        start_time = time.time()

        try:
            # Check if tmux session exists
            check_cmd = f"tmux has-session -t {self.config.tmux_session} 2>/dev/null"
            process = await asyncio.create_subprocess_shell(
                check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            returncode = await process.wait()

            response_time = (time.time() - start_time) * 1000

            if returncode == 0:
                # Check if process is actually running
                pid = await self._get_tmux_pid()

                if pid:
                    # Additional check: verify process exists
                    try:
                        import psutil
                        proc = psutil.Process(pid)
                        if proc.is_running():
                            return HealthCheckResult(
                                status=HealthStatus.HEALTHY,
                                message="Bot is running",
                                details={"pid": pid},
                                response_time_ms=response_time
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="Tmux session exists but process not found",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="Bot is not running",
                    response_time_ms=response_time
                )

        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000
            )

    async def get_metrics(self) -> ServiceMetrics:
        """Get bot metrics."""
        metrics = ServiceMetrics()

        if self._pid:
            try:
                import psutil
                process = psutil.Process(self._pid)

                with process.oneshot():
                    metrics.cpu_percent = process.cpu_percent(interval=0.1)
                    mem_info = process.memory_info()
                    metrics.memory_mb = mem_info.rss / 1024 / 1024
                    metrics.memory_percent = process.memory_percent()

                    if self._start_time:
                        metrics.uptime_seconds = int(
                            (datetime.now() - self._start_time).total_seconds()
                        )

                    metrics.restart_count = self._restart_count

                    # Custom metrics
                    metrics.custom_metrics = {
                        "tmux_session": self.config.tmux_session,
                        "log_file": self.config.log_file
                    }

            except Exception as e:
                LOG.warning(f"Could not collect metrics: {e}")

        return metrics

    async def _get_tmux_pid(self) -> Optional[int]:
        """Get PID of process running in tmux session."""
        try:
            cmd = (
                f"tmux list-panes -t {self.config.tmux_session} "
                f"-F '{{pane_pid}}' 2>/dev/null | head -1"
            )
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await process.communicate()

            if process.returncode == 0 and stdout:
                pane_pid = int(stdout.decode().strip())

                # Get child processes
                cmd2 = f"pgrep -P {pane_pid}"
                process2 = await asyncio.create_subprocess_shell(
                    cmd2,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout2, _ = await process2.communicate()

                if stdout2:
                    # Return first child PID (should be python process)
                    pids = stdout2.decode().strip().split('\n')
                    if pids:
                        return int(pids[0])

                return pane_pid

        except Exception as e:
            LOG.debug(f"Could not get tmux PID: {e}")

        return None

    async def get_logs(self, lines: int = 50) -> str:
        """Get recent bot logs."""
        log_file = Path("/root/orbitvpn") / self.config.log_file

        if not log_file.exists():
            return "Log file not found"

        try:
            cmd = f"tail -n {lines} {log_file}"
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await process.communicate()
            return stdout.decode()

        except Exception as e:
            return f"Error reading logs: {e}"
