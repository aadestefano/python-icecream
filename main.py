from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from prometheus_client import Counter, start_http_server


app = FastAPI()

class IceCreamFlavor(BaseModel):
    flavorName: str
    flavorDesc: str
    flavorPrice: float
    flavorQuantity: int
    flavorID:int

flavors = {
    0: IceCreamFlavor(flavorName="Chocolate", flavorDesc="Cocoa", flavorPrice=2.00, flavorQuantity=100, flavorID=0 ),
    1: IceCreamFlavor(flavorName="Lemon Sherbet", flavorDesc="Tangy", flavorPrice=2.50, flavorQuantity=50, flavorID=1 ),
    2: IceCreamFlavor(flavorName="Vanilla", flavorDesc="Classic", flavorPrice=1.00, flavorQuantity=200, flavorID=2 ),
}

# define endpoint counter
endpoint_counter = Counter("endpoint_usage_total", "Total number of endpoint requests", ["endpoint"])

@app.middleware("http")
async def count_requests(request: Request, call_next):
    """middleware to count endpoint reqs."""
    response = await call_next(request)
    endpoint_counter.labels(endpoint=request.url.path).inc()
    return response


@app.get("/")
def index() -> dict[str, dict[int, IceCreamFlavor]]:
    return {"flavors": flavors}

@app.get("/flavors/{flavorID}")
def queryFlavorByID(flavorID: int) -> IceCreamFlavor:
    if flavorID not in flavors:
        raise HTTPException(
            status_code=404, detail="Flavor not found"
        )
    return flavors[flavorID]

Selection = dict[
    str, str | str | float | int | int | None
]

@app.get("/flavors/")
def queryByParam(
        flavorName: str | None = None,
        flavorDesc: str | None = None,
        flavorPrice: float | None = None,
        flavorQuantity: int = None,
        flavorID: int = None,

) -> dict[str, Selection | list[IceCreamFlavor]]:
    def checkFlavor(flavor: IceCreamFlavor) -> bool:
        return all(
            (
                flavorName is None or flavor.flavorName == flavorName,
                flavorDesc is None or flavor.flavorDesc == flavorDesc,
                flavorPrice is None or flavor.flavorPrice == flavorPrice,
                flavorQuantity is None or flavor.flavorQuantity == flavorQuantity,
                flavorID is None or flavor.flavorID == flavorID,
            )
        )
    selection = [flavor for flavor in flavors.values() if checkFlavor(flavor)]
    return{
        "query": {"flavorName": flavorName, "flavorDesc": flavorDesc, "flavorPrice": flavorPrice, "flavorQuantity": flavorQuantity, "flavorID": flavorID},
        "selection": selection,
        }

@app.post("/")
def addFlavor(flavor: IceCreamFlavor) -> dict[str, IceCreamFlavor]:

    if flavor.flavorID in flavors:
        raise HTTPException(status_code=400, detail="Flavor ID already exists")
    flavors[flavor.flavorID] = flavor
    return {"added": flavor}

@app.put("/update/{flavorID}")
def updateFlavor(
        flavorID: int,
        flavorName: str | None = None,
        flavorDesc: str | None = None,
        flavorPrice: float | None = None,
        flavorQuantity: int = None,
) -> dict[str, IceCreamFlavor]:
    if flavorID not in flavors:
        raise HTTPException(status_code=404, detail="Flavor not found")
    if all(info is None for info in (flavorName, flavorPrice, flavorQuantity)):
        raise HTTPException(status_code=400, detail="No parameters provided")

    flavor = flavors[flavorID]
    if flavorName is not None:
        flavor.flavorName = flavorName
    if flavorDesc is not None:
        flavor.flavorDesc = flavorDesc
    if flavorPrice is not None:
        flavor.flavorPrice = flavorPrice
    if flavorQuantity is not None:
        flavor.flavorQuantity = flavorQuantity
    return {"updated": flavor}

@app.delete("/delete/{flavorID}")
def deleteFlavor(flavorID: int) -> dict[str, IceCreamFlavor]:
    if flavorID not in flavors:
        raise HTTPException(
            status_code=404, detail="Flavor not found"
        )
    flavor = flavors.pop(flavorID)
    return {"deleted": flavor}

#start prometheus server
start_http_server(8001)










