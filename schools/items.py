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
	address4 = Field()
	telephone = Field()
	email = Field()
	age_range = Field()
	url = Field() # optional
	category = Field() # optional


	def set_addr(self, address):
		addr = [ a.strip().strip(',') for a in address if len(a.strip()) > 0]
		if (len(addr) > 4) or (len(addr) < 2):
			self['address1'] = "WARNING: address of length {} - {}".format(len(addr), addr)
		else:
			for i,a in enumerate(addr):
				self['address{}'.format(i+1)] = a
