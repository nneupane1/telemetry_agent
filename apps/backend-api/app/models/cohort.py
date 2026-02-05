from pydantic import BaseModel, Field\nfrom typing import Dict, List\n\nclass CohortRequest(BaseModel):\n    vin_data: List[Dict] = Field(..., description=\
