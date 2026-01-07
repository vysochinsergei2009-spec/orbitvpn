from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from aiomarzban import MarzbanAPI, UserDataLimitResetStrategy

from app.settings.log import get_logger
from app.settings.config import env

LOG = get_logger(__name__)


@dataclass
class MarzbanInstance:
    id: str = "default"
    name: str = "Default Instance"
    base_url: str = field(default=env.PANEL_HOST)
    username: str = field(default=env.PANEL_USERNAME)
    password: str = field(default=env.PANEL_PASSWORD)
    is_active: bool = True
    priority: int = 1
    excluded_node_names: Optional[List[str]] = None


@dataclass
class NodeLoadMetrics:
    node_id: int
    node_name: str
    active_users: int
    usage_coefficient: float
    uplink: int
    downlink: int
    instance_id: str

    @property
    def load_score(self) -> float:
        total_traffic_gb = (self.uplink + self.downlink) / (1024 ** 3)

        user_weight = 100.0
        traffic_weight = 1.0

        score = (
            (self.active_users * user_weight * self.usage_coefficient) +
            (total_traffic_gb * traffic_weight)
        )

        return score


class MarzbanClient:
    def __init__(self):
        self._instances_cache: Dict[str, MarzbanAPI] = {}
        self._instance = MarzbanInstance()

    def _get_active_instances(self) -> List[MarzbanInstance]:
        return [self._instance]

    def _get_or_create_api(self, instance: MarzbanInstance) -> MarzbanAPI:
        if instance.id not in self._instances_cache:
            self._instances_cache[instance.id] = MarzbanAPI(
                address=instance.base_url,
                username=instance.username,
                password=instance.password,
                default_proxies={"vless": {"flow": ""}}
            )
        return self._instances_cache[instance.id]

    async def _get_node_metrics(
        self,
        instance: MarzbanInstance,
        api: MarzbanAPI
    ) -> List[NodeLoadMetrics]:
        from app.db.cache import get_redis
        import json

        redis_key = f"marzban:{instance.id}:node_metrics"

        try:
            redis = await get_redis()
            cached = await redis.get(redis_key)
            if cached:
                cached_data = json.loads(cached)
                return [
                    NodeLoadMetrics(
                        node_id=m['node_id'],
                        node_name=m['node_name'],
                        active_users=m['active_users'],
                        usage_coefficient=m['usage_coefficient'],
                        uplink=m['uplink'],
                        downlink=m['downlink'],
                        instance_id=m['instance_id']
                    )
                    for m in cached_data
                ]
        except Exception as e:
            LOG.warning(f"Redis error reading node metrics for {instance.id}: {e}")

        try:
            try:
                nodes = await api.get_nodes()
            except Exception as e:
                LOG.debug(f"Nodes API not available for instance {instance.id}: {e}")
                return []

            excluded_names = instance.excluded_node_names or []
            if excluded_names:
                original_count = len(nodes)
                nodes = [n for n in nodes if n.name not in excluded_names]
                if len(nodes) < original_count:
                    LOG.info(f"Excluded {original_count - len(nodes)} node(s) from instance {instance.id}: {excluded_names}")

            if not nodes:
                LOG.warning(f"All nodes excluded for instance {instance.id}")
                return []

            usage_map = {}
            try:
                usage_response = await api.get_nodes_usage()
                usage_map = {
                    u.node_id: u for u in usage_response.usages
                    if u.node_id is not None
                }
            except Exception as e:
                LOG.debug(f"Node usage API not available for instance {instance.id}: {e}")

            try:
                users = await api.get_users(limit=10000)
                total_active_users = sum(1 for u in users.users if u.status == 'active')
            except Exception as e:
                LOG.debug(f"Failed to get users for instance {instance.id}: {e}")
                total_active_users = 0

            node_count = len(nodes)
            avg_users_per_node = total_active_users / node_count if node_count > 0 else 0

            metrics = []
            for node in nodes:
                usage = usage_map.get(node.id)
                uplink = usage.uplink if usage else 0
                downlink = usage.downlink if usage else 0

                metrics.append(NodeLoadMetrics(
                    node_id=node.id,
                    node_name=node.name,
                    active_users=int(avg_users_per_node),
                    usage_coefficient=node.usage_coefficient or 1.0,
                    uplink=uplink,
                    downlink=downlink,
                    instance_id=instance.id
                ))

            try:
                redis = await get_redis()
                cache_data = [
                    {
                        'node_id': m.node_id,
                        'node_name': m.node_name,
                        'active_users': m.active_users,
                        'usage_coefficient': m.usage_coefficient,
                        'uplink': m.uplink,
                        'downlink': m.downlink,
                        'instance_id': m.instance_id
                    }
                    for m in metrics
                ]
                await redis.setex(redis_key, 120, json.dumps(cache_data))
            except Exception as e:
                LOG.warning(f"Redis error caching node metrics for {instance.id}: {e}")

            return metrics

        except Exception as e:
            LOG.error(f"Failed to get node metrics for instance {instance.id}: {e}")
            return []

    async def get_best_instance_and_node(
        self,
        manual_instance_id: Optional[str] = None
    ) -> Tuple[MarzbanInstance, MarzbanAPI, Optional[int]]:
        instance = self._instance

        if not instance.is_active:
            raise ValueError("No active Marzban instances available")

        api = self._get_or_create_api(instance)
        
        all_metrics: List[NodeLoadMetrics] = await self._get_node_metrics(instance, api)

        if not all_metrics:
            LOG.warning("No node metrics available, using instance without node selection")
            return instance, api, None

        all_metrics.sort(key=lambda m: m.load_score)
        best_metric = all_metrics[0]

        LOG.info(
            f"Selected node {best_metric.node_name} (ID: {best_metric.node_id}) "
            f"on instance {instance.id} with load score {best_metric.load_score:.2f}"
        )

        return instance, api, best_metric.node_id

    async def add_user(
        self,
        username: str,
        days: int,
        data_limit: int = 0,
        max_ips: Optional[int] = None,
        manual_instance_id: Optional[str] = None
    ):
        instance, api, node_id = await self.get_best_instance_and_node(manual_instance_id)

        if max_ips is None:
            max_ips = env.MAX_IPS_PER_CONFIG

        try:

            from aiomarzban.models import UserCreate, UserStatusCreate
            from aiomarzban.utils import future_unix_time, gb_to_bytes
            from aiomarzban.enums import Methods

            expire = future_unix_time(days=days)

            user_data = UserCreate(
                proxies=api.default_proxies,
                expire=expire,
                data_limit=gb_to_bytes(data_limit),
                data_limit_reset_strategy=UserDataLimitResetStrategy.month,
                inbounds=api.default_inbounds,
                username=username,
                status=UserStatusCreate.active,
            )

            payload = user_data.model_dump()
            payload['ip_limit'] = max_ips

            resp = await api._request(Methods.POST, "/user", data=payload)

            from aiomarzban.models import UserResponse
            new_user = UserResponse(**resp)

            if not new_user.links:
                raise ValueError("No VLESS link returned from Marzban")

            LOG.info(
                f"Created user {username} on instance {instance.id} "
                f"(target node: {node_id if node_id else 'auto'}, max_ips: {max_ips})"
            )

            return new_user

        except Exception as e:
            LOG.error(f"Failed to add user {username} on instance {instance.id}: {e}")
            raise

    async def remove_user(self, username: str, instance_id: Optional[str] = None):
        instance = self._instance
        try:
            api = self._get_or_create_api(instance)
            await api.remove_user(username)
            LOG.info(f"Removed user {username} from instance {instance.id}")
            return
        except Exception as e:
            LOG.warning(f"User {username} not found on instance {instance.id}: {e}")


    async def get_user(self, username: str, instance_id: Optional[str] = None):
        instance = self._instance
        try:
            api = self._get_or_create_api(instance)
            user = await api.get_user(username)
            return user
        except Exception:
            return None


    async def modify_user(
        self,
        username: str,
        instance_id: Optional[str] = None,
        max_ips: Optional[int] = None,
        **kwargs
    ):
        instance = self._instance
        try:
            api = self._get_or_create_api(instance)

            if max_ips is not None:
                from aiomarzban.models import UserModify
                from aiomarzban.utils import gb_to_bytes
                from aiomarzban.enums import Methods

                if 'data_limit' in kwargs and kwargs['data_limit'] is not None:
                    kwargs['data_limit'] = gb_to_bytes(kwargs['data_limit'])

                user_data = UserModify(**kwargs)

                payload = user_data.model_dump(exclude_none=True)
                payload['ip_limit'] = max_ips

                await api._request(Methods.PUT, f"/user/{username}", data=payload)
                LOG.info(f"Modified user {username} on instance {instance.id} (max_ips: {max_ips})")
            else:
                await api.modify_user(username, **kwargs)
                LOG.info(f"Modified user {username} on instance {instance.id}")

            return
        except Exception:
            raise ValueError(f"User {username} not found on instance {instance.id}")

