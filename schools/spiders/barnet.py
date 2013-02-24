from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy import log # only used for levels

from schools.items import School

class BarnetSpider(CrawlSpider):
	name = "barnet"
	allowed_domains = ["www.{}.gov.uk".format(name)]
	start_urls = [
			"http://www.barnet.gov.uk/directory/10/a_to_z/a"
	]
	# There are a load of supplementary schools, but they are in a pdf: http://www.ealing.gov.uk/info/200086/schools_and_colleges/144/supplementary_schools

	# crawl the a to z listings (primary and secondary), and parse the two types of school url
	rules = [
		Rule(SgmlLinkExtractor(allow="directory/10/a_to_z/"), follow=True),
		Rule(SgmlLinkExtractor(allow="directory_record"), callback='parse_school')
	]

	mapping = {
		'name':'name',
		'school':'name',
		'head teacher':'head',
		'headteacher':'head',
		'acting headteacher':'head',
		'executive head':'head',
		'telephone':'telephone',
		'email':'email',
		'website':'url',
		'age range':'age_range',
		'type':'category',
		'type of school':'category',
		'school type':'category'
	}

	ignore = [
		'dfe number', 'dfe code', 'chair of governors', 'fax',
		'ward', 'religion', 'nursery places', 'gender', 
		'map', 'number of nursery places', 
		'planned admission limit at 4 years',
		'uniform', 'breakfast club', 'after school club',
		'admissions policies', 'achievement and attainment',
		'prospectus information', 'school ofsted report',
		'ofsted report', 'nursery class',
		'admissions policies and sifs', 'travel',
		'planned admission limit at 7 years',
		'performance post-16', 'performance',
		'high school prospectus', 'denomination',
		'sif form for admission', 'location',
		'priority area map'
	]

	def parse_school(self, response):
		hxs = HtmlXPathSelector(response)
		# All data is in a table, with th being the label, td the data

		school = School()
		addr = []
		addr_most_recent = False

		rows = hxs.select('//div[@class="serviceDetails"]//table/tr')
		for row in rows:
			label = row.select('th/text()').extract()
			if label:
				label = label[0].strip().strip(':').lower()
				addr_most_recent = False # there's a label, so we're no longer on the address rows
			value = row.select('td/text() | td/a/text()').extract()

			if label and (label in self.mapping):
				if value:
					school[self.mapping[label]] = value[0].strip()
				else:
					self.log("No value found for {} for {}".format(label, school['name']), log.WARNING)
			elif (label == "address") or (label == [] and addr_most_recent) or (label == "postcode"):
				addr += value[0].split('\n')
				addr_most_recent = True # the following items are address items (not strictly true in the postcode case, but just assume that postcode isn't followed by a blank label)
			
			elif (label not in self.ignore) and not (value == ['View larger map']):
				self.log("Discarding '{}' from '{}' as not found in mapping, value was: {}".format(label, school["name"], value), level=log.WARNING)
			else:
				pass

		school.set_addr(addr)
		return school

