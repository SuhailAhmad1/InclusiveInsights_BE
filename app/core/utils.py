from fastapi.responses import JSONResponse

def response_json(data, message: str, status_code: int = 200):
    return JSONResponse(content={"data": data, "message": message}, status_code=status_code)
