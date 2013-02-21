# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class School(Item):
	name = Field()
	head = Field()
	address1 = Field()
	address2 = Field()
	address3 = Field()
	telephone = Field()
	email = Field()
	age_range = Field()
	url = Field() # optional
	category = Field() # optional
