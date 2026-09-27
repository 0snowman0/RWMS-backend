from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def application_lifespan(
    app: FastAPI,
):

    # =========================================================
    # Startup
    # =========================================================

    if hasattr(app.state, "log_worker"):
        await app.state.log_worker.start()

    if hasattr(app.state, "audit_log_worker"):
        await app.state.audit_log_worker.start()

    try:

        yield

    finally:

        # =====================================================
        # Shutdown
        # =====================================================

        if hasattr(app.state, "audit_log_worker"):
            await app.state.audit_log_worker.stop()

        if hasattr(app.state, "log_worker"):
            await app.state.log_worker.stop()