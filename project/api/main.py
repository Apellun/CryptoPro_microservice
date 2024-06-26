import uvicorn
from fastapi import FastAPI, status
from project.api.core.exceptions import UniqueConstraintError, DatabaseError, EntityNotFoundError
from organizations.router import organizations_router
from server_settings.router import server_router
from project.api.config import cwd
from project.api.core.exception_handler import create_exception_handler


app = FastAPI(
    title="Crypto API"
)
app.include_router(organizations_router, prefix="/organizations")
app.include_router(server_router, prefix="/server_settings")


app.add_exception_handler(
    exc_class_or_status_code=UniqueConstraintError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, "Некорректный запрос"
    ),
)
app.add_exception_handler(
    exc_class_or_status_code=DatabaseError,
    handler=create_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Внутренняя ошибка сервера"
    ),
)
app.add_exception_handler(
    exc_class_or_status_code=EntityNotFoundError,
    handler=create_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Внутренняя ошибка сервера"
    ),
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
            host='0.0.0.0',
            port=9080,
            reload=True,
            workers=3,
            log_config=f"{cwd}\\log.ini"
        )