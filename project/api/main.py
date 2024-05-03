import uvicorn
import pathlib
from fastapi import FastAPI
from crypto_manager.router import crypto_manager_router


app = FastAPI(
    title="Подписи API"
)
app.include_router(crypto_manager_router)


if __name__ == "__main__":
    cwd = pathlib.Path(__file__).parent.resolve()
    uvicorn.run(
        "main:app",
            host='0.0.0.0',
            port=8080,
            reload=True,
            workers=3,
            # log_config=f"{cwd}\\log.ini"
        )