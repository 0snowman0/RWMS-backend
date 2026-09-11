from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def application_lifespan(
    app: FastAPI,
):

    # =========================================================
    # Startup
    # =========================================================

    await app.state.log_worker.start()

    try:

        yield

    finally:

        # =====================================================
        # Shutdown
        # =====================================================

        await app.state.log_worker.stop()