from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log # only used for levels

from schools.items import School

class HarrowSpider(BaseSpider):
	name = "harrow"
	allowed_domains = ["harrow.gov.uk"]
	start_urls = [
		"http://www.harrow.gov.uk/site/custom_scripts/php/myharrow/print/mhnearest_schools_print.php?n=100021303037&cat=primaryschools&sort=alpha&catdesc=Primary%20Schools%C2%A0&dist=0"
	]

	mapping = {
		'headteacher':'head',
		'telephone':'telephone',
		'email':'email',
		'web address':'url'
	}

	# All the "prow" divs up until a "spacer" div are data for one school
	# col4 is the school name
	# All the col1 spans are the address
	# col2 spans are just labels for col3 data
	# col3, in order: headteacher, chair, null, telephone, fax, email, url, dfe number
	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		divs = hxs.select('//div[@id="pageInfo"]//div')

		school = School()
		schools = []
		address = []
		for div in divs:
			if div.select('@class').extract()[0] == 'spacer':
				# finished previous school
				# the final school does have a spacer after it
				self.set_addr(school, address)
				school['age_range'] = 'Primary'
				schools.append(school)
				address = []
				school = School()
			elif div.select('@class').extract()[0] == 'prow':
				name = div.select('span[@class="col4"]/b/text()').extract()
				if name:
					school['name'] = name[0].strip()
				spans = div.select('span')

				addr = div.select('span[@class="col1"]/text()').extract()
				if addr:
					address.append(addr[0].strip())

				col3 =  div.select('span[@class="col3"]//text()').extract()
				if col3 and col3[0].strip():
					label = div.select('span[@class="col2"]//text()').extract()[0].strip().lower()
					if label in self.mapping:
						school[self.mapping[label]] = col3[0].strip()
					else:
						self.log("Discarding '{}' as not found in mapping".format(label), level=log.DEBUG)

				
		return schools

	def set_addr(self, school, address):
		addr = [ a.strip() for a in address if len(a.strip()) > 0]
		if len(addr) != 3:
			self.log("School '{}' had an address of length {} - discarding: {}".format(school['name'], len(addr), addr),log.WARNING)
		else:
			for i,a in enumerate(addr):
				#self.log("setting address{} to {}".format(i,a))
				school['address{}'.format(i+1)] = a
