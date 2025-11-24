#!/usr/bin/env python3
"""
VPN Performance Diagnostic Script
Analyzes Marzban server load, user distribution, and identifies bottlenecks
"""

import asyncio
import sys
from typing import Dict, List
from datetime import datetime
from aiomarzban import MarzbanAPI
from tabulate import tabulate

# Configuration from .env
MARZBAN_URL = "https://s001.orbitcorp.space:8000/"
MARZBAN_USERNAME = "sanenh"
MARZBAN_PASSWORD = "8457"


class VPNDiagnostics:
    def __init__(self):
        self.api = MarzbanAPI(
            address=MARZBAN_URL,
            username=MARZBAN_USERNAME,
            password=MARZBAN_PASSWORD,
            default_proxies={"vless": {"flow": ""}}
        )
        self.results = {}

    async def get_system_stats(self):
        """Get overall Marzban system statistics"""
        try:
            stats = await self.api.get_system_stats()
            self.results['system'] = {
                'total_users': stats.total_user,
                'active_users': stats.users_active,
                'incoming_bandwidth': stats.incoming_bandwidth,
                'outgoing_bandwidth': stats.outgoing_bandwidth,
                'incoming_bandwidth_speed': stats.incoming_bandwidth_speed,
                'outgoing_bandwidth_speed': stats.outgoing_bandwidth_speed,
            }
            return stats
        except Exception as e:
            print(f"❌ Failed to get system stats: {e}")
            return None

    async def get_node_info(self):
        """Get detailed node information and load metrics"""
        try:
            nodes = await self.api.get_nodes()

            if not nodes:
                print("⚠️  No nodes found. Check Marzban configuration.")
                return []

            # Get node usage statistics
            try:
                usage_response = await self.api.get_nodes_usage()
                usage_map = {u.node_id: u for u in usage_response.usages if u.node_id is not None}
            except Exception as e:
                print(f"⚠️  Node usage API not available: {e}")
                usage_map = {}

            node_data = []
            for node in nodes:
                usage = usage_map.get(node.id)

                node_info = {
                    'id': node.id,
                    'name': node.name,
                    'status': node.status,
                    'address': node.address,
                    'port': node.port,
                    'usage_coefficient': node.usage_coefficient or 1.0,
                    'uplink_gb': (usage.uplink / (1024**3)) if usage else 0,
                    'downlink_gb': (usage.downlink / (1024**3)) if usage else 0,
                }
                node_data.append(node_info)

            self.results['nodes'] = node_data
            return node_data

        except Exception as e:
            print(f"❌ Failed to get node info: {e}")
            return []

    async def get_user_distribution(self):
        """Get user count and analyze distribution"""
        try:
            # Fetch all users
            users_response = await self.api.get_users(limit=10000)
            users = users_response.users

            # Analyze user status
            status_counts = {
                'active': 0,
                'disabled': 0,
                'limited': 0,
                'expired': 0,
                'on_hold': 0
            }

            total_data_used = 0
            users_by_traffic = []

            for user in users:
                status_counts[user.status] = status_counts.get(user.status, 0) + 1

                # Calculate data usage
                data_used_gb = user.used_traffic / (1024**3) if user.used_traffic else 0
                total_data_used += data_used_gb

                if user.status == 'active':
                    users_by_traffic.append({
                        'username': user.username,
                        'data_used_gb': data_used_gb,
                        'data_limit_gb': user.data_limit / (1024**3) if user.data_limit else 0,
                        'online_at': user.online_at
                    })

            # Sort by traffic usage
            users_by_traffic.sort(key=lambda x: x['data_used_gb'], reverse=True)

            self.results['users'] = {
                'total': len(users),
                'status_distribution': status_counts,
                'total_data_used_gb': total_data_used,
                'top_users': users_by_traffic[:20]  # Top 20 heavy users
            }

            return users_by_traffic

        except Exception as e:
            print(f"❌ Failed to get user distribution: {e}")
            return []

    async def check_database_health(self):
        """Check database for inconsistencies"""
        try:
            import asyncpg

            conn = await asyncpg.connect(
                host='127.0.0.1',
                user='orbitcorp',
                password='3hdS83ru9g29',
                database='orbitvpn'
            )

            # Count configs
            total_configs = await conn.fetchval('SELECT COUNT(*) FROM configs WHERE deleted = false')

            # Count users with active subscriptions
            active_subs = await conn.fetchval(
                'SELECT COUNT(*) FROM users WHERE subscription_end > NOW()'
            )

            # Find orphaned configs (users without active sub but with configs)
            orphaned = await conn.fetchval('''
                SELECT COUNT(DISTINCT c.tg_id)
                FROM configs c
                LEFT JOIN users u ON c.tg_id = u.tg_id
                WHERE c.deleted = false
                AND (u.subscription_end IS NULL OR u.subscription_end < NOW())
            ''')

            await conn.close()

            self.results['database'] = {
                'total_configs': total_configs,
                'active_subscriptions': active_subs,
                'orphaned_configs': orphaned
            }

        except Exception as e:
            print(f"❌ Database health check failed: {e}")

    def print_report(self):
        """Print comprehensive diagnostic report"""
        print("\n" + "="*80)
        print("🔍 OrbitVPN Performance Diagnostic Report")
        print("="*80)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # System Stats
        if 'system' in self.results:
            sys_stats = self.results['system']
            print("📊 SYSTEM STATISTICS")
            print("-" * 80)
            print(f"  Total Users:     {sys_stats['total_users']}")
            print(f"  Active Users:    {sys_stats['active_users']}")
            print(f"  Incoming Speed:  {sys_stats['incoming_bandwidth_speed'] / (1024**2):.2f} MB/s")
            print(f"  Outgoing Speed:  {sys_stats['outgoing_bandwidth_speed'] / (1024**2):.2f} MB/s")
            print(f"  Total Incoming:  {sys_stats['incoming_bandwidth'] / (1024**3):.2f} GB")
            print(f"  Total Outgoing:  {sys_stats['outgoing_bandwidth'] / (1024**3):.2f} GB")
            print()

        # Node Information
        if 'nodes' in self.results and self.results['nodes']:
            print("🖥️  NODE INFORMATION")
            print("-" * 80)

            node_table = []
            for node in self.results['nodes']:
                node_table.append([
                    node['name'],
                    node['status'],
                    f"{node['address']}:{node['port']}",
                    f"{node['usage_coefficient']:.2f}",
                    f"{node['uplink_gb']:.2f}",
                    f"{node['downlink_gb']:.2f}",
                    f"{node['uplink_gb'] + node['downlink_gb']:.2f}"
                ])

            print(tabulate(
                node_table,
                headers=['Node', 'Status', 'Address', 'Coeff', 'Upload (GB)', 'Download (GB)', 'Total (GB)'],
                tablefmt='grid'
            ))
            print()

        # User Distribution
        if 'users' in self.results:
            user_stats = self.results['users']
            print("👥 USER DISTRIBUTION")
            print("-" * 80)
            print(f"  Total Users: {user_stats['total']}")

            status_table = [[k.capitalize(), v] for k, v in user_stats['status_distribution'].items()]
            print(tabulate(status_table, headers=['Status', 'Count'], tablefmt='simple'))
            print(f"\n  Total Data Used: {user_stats['total_data_used_gb']:.2f} GB")
            print()

            # Top bandwidth users
            if user_stats['top_users']:
                print("  🔥 TOP 10 BANDWIDTH CONSUMERS:")
                top_table = []
                for i, user in enumerate(user_stats['top_users'][:10], 1):
                    usage_percent = (user['data_used_gb'] / user['data_limit_gb'] * 100) if user['data_limit_gb'] > 0 else 0
                    top_table.append([
                        i,
                        user['username'][:20],
                        f"{user['data_used_gb']:.2f}",
                        f"{user['data_limit_gb']:.2f}",
                        f"{usage_percent:.1f}%"
                    ])

                print(tabulate(
                    top_table,
                    headers=['#', 'Username', 'Used (GB)', 'Limit (GB)', 'Usage %'],
                    tablefmt='simple'
                ))
            print()

        # Database Health
        if 'database' in self.results:
            db_stats = self.results['database']
            print("💾 DATABASE HEALTH")
            print("-" * 80)
            print(f"  Total Configs:         {db_stats['total_configs']}")
            print(f"  Active Subscriptions:  {db_stats['active_subscriptions']}")
            print(f"  Orphaned Configs:      {db_stats['orphaned_configs']}")

            if db_stats['orphaned_configs'] > 0:
                print(f"\n  ⚠️  Warning: {db_stats['orphaned_configs']} configs exist for expired subscriptions")
            print()

        # Recommendations
        self.print_recommendations()

    def print_recommendations(self):
        """Print optimization recommendations based on diagnostics"""
        print("💡 RECOMMENDATIONS")
        print("-" * 80)

        recommendations = []

        # Check system load
        if 'system' in self.results:
            sys_stats = self.results['system']
            active_ratio = sys_stats['active_users'] / sys_stats['total_users'] if sys_stats['total_users'] > 0 else 0

            if active_ratio > 0.7:
                recommendations.append(
                    "🔴 HIGH LOAD: Over 70% of users are active. Consider adding more nodes/servers."
                )

            # Check bandwidth
            total_speed_mbps = (sys_stats['incoming_bandwidth_speed'] + sys_stats['outgoing_bandwidth_speed']) / (1024**2)
            if total_speed_mbps > 800:  # Assuming 1Gbps connection
                recommendations.append(
                    f"🔴 HIGH BANDWIDTH: Current speed {total_speed_mbps:.0f} MB/s. Upgrade network capacity."
                )

        # Check node distribution
        if 'nodes' in self.results and len(self.results['nodes']) == 1:
            recommendations.append(
                "⚠️  SINGLE NODE: All traffic goes through one node. Add multiple nodes for load balancing."
            )

        # Check user status
        if 'users' in self.results:
            user_stats = self.results['users']
            limited_count = user_stats['status_distribution'].get('limited', 0)

            if limited_count > user_stats['total'] * 0.1:
                recommendations.append(
                    f"⚠️  TRAFFIC LIMITS: {limited_count} users hit data limits. Consider increasing default limits."
                )

        # Check database
        if 'database' in self.results:
            if self.results['database']['orphaned_configs'] > 10:
                recommendations.append(
                    "🧹 CLEANUP: Run cleanup script to remove configs for expired subscriptions."
                )

        # General recommendations
        recommendations.extend([
            "✅ Enable Redis caching if not already enabled (TTL: 300s for user data)",
            "✅ Monitor node performance: check excluded_node_names in marzban_instances table",
            "✅ Consider multi-instance setup: Add secondary Marzban server for load distribution",
            "✅ Review MAX_IPS_PER_CONFIG: Lower value = less concurrent connections per user",
            "✅ Implement rate limiting on payment/config creation endpoints"
        ])

        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

        print("\n" + "="*80)

    async def run_diagnostics(self):
        """Run all diagnostic checks"""
        print("🚀 Starting VPN diagnostics...\n")

        await self.get_system_stats()
        await self.get_node_info()
        await self.get_user_distribution()
        await self.check_database_health()

        self.print_report()


async def main():
    diagnostics = VPNDiagnostics()
    await diagnostics.run_diagnostics()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostics interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
