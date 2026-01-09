#!/bin/bash


readonly TMUX_SESSION="orbitvpn_bot"
readonly PROJECT_DIR="/opt/orbitvpn"

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color
readonly BOLD='\033[1m'


print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════╗"
    echo "║        OrbitVPN Bot Manager            ║"
    echo "║            Stopping Bot...             ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}


print_banner

if ! tmux has-session -t "${TMUX_SESSION}" 2>/dev/null; then
    print_warning "Bot session '${TMUX_SESSION}' is not running"
    print_info "Nothing to stop"
    exit 0
fi

print_info "Found active session: ${TMUX_SESSION}"
print_info "Sending graceful shutdown signal..."

tmux send-keys -t "${TMUX_SESSION}" C-c

sleep 2

if tmux has-session -t "${TMUX_SESSION}" 2>/dev/null; then
    print_warning "Bot did not stop gracefully, forcing termination..."
    tmux kill-session -t "${TMUX_SESSION}"
    sleep 1
fi

if ! tmux has-session -t "${TMUX_SESSION}" 2>/dev/null; then
    print_success "Bot stopped successfully"
    echo ""
    print_info "To start the bot again, run: ./boton.sh"
    echo ""
else
    print_error "Failed to stop the bot session"
    print_info "Try manually: tmux kill-session -t ${TMUX_SESSION}"
    exit 1
fi
