
from typing import List, Protocol, Dict, Any
from app.application.listing.dtos import ListingResponse

class ListingDataProvider(Protocol):
    def get_stocks(self) -> List[Dict[str, Any]]: ...
    def get_etfs(self) -> List[Dict[str, Any]]: ...
    def get_industries(self) -> List[Dict[str, Any]]: ...
    def get_industries_icb(self) -> List[Dict[str, Any]]: ...

class ListingService:
    def __init__(self, data_provider: ListingDataProvider):
        self.data_provider = data_provider

    def get_stocks(self) -> ListingResponse:
        data = self.data_provider.get_stocks()
        return ListingResponse(count=len(data), data=data)

    def get_etfs(self) -> ListingResponse:
        data = self.data_provider.get_etfs()
        return ListingResponse(count=len(data), data=data)

    def get_industries(self) -> ListingResponse:
        data = self.data_provider.get_industries()
        return ListingResponse(count=len(data), data=data)

    def get_industries_icb(self) -> ListingResponse:
        data = self.data_provider.get_industries_icb()
        return ListingResponse(count=len(data), data=data)
