from .commands import router as commands_router
from .photo import router as photo_router
from .video import router as video_router

def setup_routers(dp):
    dp.include_router(commands_router)
    dp.include_router(photo_router)
    dp.include_router(video_router)
