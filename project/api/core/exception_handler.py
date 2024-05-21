import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from project.api.core.exceptions import CryptoApiError


def create_exception_handler(status_code: int, initial_detail: str):
    detail = {"message": initial_detail}

    async def exception_handler(_: Request, exc: CryptoApiError) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message

        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        if exc.details:
            detail["details"] = exc.details

        logging.exception(exc)

        return JSONResponse(
            status_code=status_code, content={
                "message": detail["message"]
            }
        )

    return exception_handler