from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy import log # only used for levels

from schools.items import School

class EalingSpider(CrawlSpider):
	name = "ealing"
	allowed_domains = ["www.{}.gov.uk".format(name)]
	start_urls = [
			"http://www.ealing.gov.uk/directory/15/a_to_z/a", # primary
			"http://www.ealing.gov.uk/info/200086/schools_and_colleges/141/sixth_forms_and_colleges/2",
			"http://www.ealing.gov.uk/directory/5/high_schools"
			# "http://www.ealing.gov.uk/info/200566/special_schools", # different presentation
	]
	# There are a load of supplementary schools, but they are in a pdf: http://www.ealing.gov.uk/info/200086/schools_and_colleges/144/supplementary_schools

	# crawl the a to z listings (primary and secondary), and parse the two types of school url
	rules = [
		Rule(SgmlLinkExtractor(allow="directory/(15|5)/a_to_z/"), follow=True),
		Rule(SgmlLinkExtractor(allow=["directory_record", "info/.*special_schools/"]), callback='parse_school')
	]

	mapping = {
		'name':'name',
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
		'dfe number', 'chair of governors', 'fax',
		'ward', 'religion', 'nursery places', 'gender', 
		'map', 'number of nursery places', 
		'planned admission limit at 4 years',
		'uniform', 'breakfast club', 'after school club',
		'admissions policies', 'achievement and attainment',
		'prospectus information', 'school ofsted report',
		'admissions policies and sifs', 'travel',
		'planned admission limit at 7 years',
		'performance post-16', 'performance',
		'high school prospectus'
	]

	def parse_school(self, response):
		hxs = HtmlXPathSelector(response)
		# All data is in a table, with th being the label, td the data

		school = School()
		addr = []
		postcode = ""

		rows = hxs.select('//table[@summary = "directory record details"]/tr')
		for row in rows:
			label = row.select('th/text()').extract()
			if not label: continue # missing label
			label = label[0].strip().strip(':').lower()
			value = row.select('td/text() | td/a/text()').extract()

			if label in self.mapping:
				if value:
					school[self.mapping[label]] = value[0].strip()
				else:
					self.log("No value found for {} for {}".format(label, school['name']), log.WARNING)
			elif label == "address":
				addr = value[0].split(",")
			elif label == "postcode":
				postcode = value[0]
			elif label not in self.ignore:
				self.log("Discarding '{}' as not found in mapping".format(label), level=log.WARNING)
			else:
				pass

		school.set_addr(addr + [postcode])
		return school

