from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy(request: Request, path: str):
    url = f"http://localhost:8000/{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    
    body = await request.body()
    
    async with httpx.AsyncClient() as client:
        if request.method == "GET":
            resp = await client.get(url, headers=headers, params=request.query_params, timeout=30)
        elif request.method == "POST":
            resp = await client.post(url, headers=headers, json=await request.json() if body else None, params=request.query_params, timeout=30)
        elif request.method == "PUT":
            resp = await client.put(url, headers=headers, json=await request.json() if body else None, params=request.query_params, timeout=30)
        elif request.method == "DELETE":
            resp = await client.delete(url, headers=headers, params=request.query_params, timeout=30)
        else:
            resp = await client.request(request.method, url, headers=headers, content=body, params=request.query_params, timeout=30)
    
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
