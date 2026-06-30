"""Outbound adapters: concrete implementations of outbound ports.

Empty until the first integration. Group each integration in its own subpackage
(e.g. `clock/`, `db/`) and ship an in-memory implementation alongside the real
one so it doubles as a test fake and a dependency-free local mode.
"""
