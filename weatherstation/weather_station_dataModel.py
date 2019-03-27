from typing import List
import os, sys

from oef.query import Eq, Range, Constraint, Query, AttributeSchema
from oef.schema import DataModel, Description , Location


class WEATHER_STATION_DATAMODEL (DataModel):
	ATTRIBUTE_COUNTRY = AttributeSchema("country", str, True, "Country")
	ATTRIBUTE_CITY = AttributeSchema("city", str, True, "City")
	
	def __init__(self):
		super().__init__("weatherStation_datamodel",[self.ATTRIBUTE_COUNTRY,
									  	 			 self.ATTRIBUTE_CITY],
									  	 			 "A localizable weather agent")