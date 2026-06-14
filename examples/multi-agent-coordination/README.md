# Multi-Agent Coordination Example

A multi-agent coordination simulation applying supervisor and peer-to-peer patterns.

## Overview
Demonstrates dynamic agent interaction topology.

## Core Design
- **Supervisor pattern**: Central router assigns tasks to specialized workers.
- **Peer-to-peer pattern**: Workers call one another directly when their respective capabilities match the subtask.
- **Shared-file handoffs**: The supervisor writes compact task briefs to a shared filesystem location; workers read only their slice, keeping each context lean.
