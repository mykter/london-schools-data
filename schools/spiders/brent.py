from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy import log # only used for levels

from schools.items import School

class BrentSpider(CrawlSpider):
	name = "brent"
	allowed_domains = ["{}.gov.uk".format(name)]
	start_urls = [
			"https://www.brent.gov.uk/schools"
	]

	# Parse all the pages linked to in the central ip2 div to urls including "Schools/"
	rules = [Rule(SgmlLinkExtractor(allow="Schools/", restrict_xpaths='//div[@class="ip2"]'), callback='parse_school')]

	mapping = {
		'head teacher':'head',
		'acting headteacher':'head',
		'executive head':'head',
		'telephone':'telephone',
		'email':'email',
		'website':'url',
		'age range':'age_range',
		'type':'category'
	}

	ignore = [
		'dfe number', 'chair of governors', 'fax',
		'ward', 'religion', 'nursery places', 'gender'
	]

	def parse_school(self, response):
		hxs = HtmlXPathSelector(response)
		# All data is preceded by the label in <strong> tags

		school = School()
		school['name'] = hxs.select('//title/text()').extract()[0].strip()

		divs = hxs.select('//div[@class="ip"]//div[strong]')
		for div in divs:
			label = div.select('strong/text()').extract()[0].strip().strip(':').lower()
			value = div.select('text() | a/text()').extract()
			if label in self.mapping:
				if value:
					school[self.mapping[label]] = value[0].strip()
				else:
					self.log("No value found for {} for {}".format(label, school['name']), log.WARNING)
			elif label == "address":
				school.set_addr(value)
			elif label not in self.ignore:
				self.log("Discarding '{}' as not found in mapping".format(label), level=log.WARNING)
			else:
				pass
		
		return school

