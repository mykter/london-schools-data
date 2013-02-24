from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log # only used for levels

from schools.items import School

class HarrowSpider(BaseSpider):
	name = "harrow"
	allowed_domains = ["{}.gov.uk".format(name)]
	start_urls = [
		"http://www.harrow.gov.uk/site/custom_scripts/php/myharrow/print/mhnearest_schools_print.php?n=100021303037&cat=primaryschools&sort=alpha&catdesc=Primary%20Schools%C2%A0&dist=0",
		"http://www.harrow.gov.uk/site/custom_scripts/php/myharrow/print/mhnearest_schools_print.php?n=200000303697&cat=highschools&sort=alpha&catdesc=&nbsp;&dist=0",
		"http://www.harrow.gov.uk/site/custom_scripts/php/myharrow/print/mhnearest_schools_print.php?n=200000303697&cat=college&sort=alpha&catdesc=&nbsp;&dist=0",
		"http://www.harrow.gov.uk/site/custom_scripts/php/myharrow/print/mhnearest_schools_print.php?n=200000303697&cat=specialSchools&sort=alpha&catdesc=&nbsp;&dist=0"
	]

	mapping = {
		'headteacher':'head',
		'acting headteacher':'head',
		'executive head':'head',
		'telephone':'telephone',
		'email':'email',
		'web address':'url'
	}

	ignore = ['fax', 'chair of governors', 'la/dfe no:']

	# All the "prow" divs up until a "spacer" div are data for one school
	# col4 is the school name
	# All the col1 spans are the address
	# col2 spans are just labels for col3 data
	# col3, in order: headteacher, chair, null, telephone, fax, email, url, dfe number
	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		divs = hxs.select('//div[@id="pageInfo"]//div')


		if "highschool" in response.url:
			age_range = "secondary"
		elif "primaryschool" in response.url:
			age_range = "primary"
			self.log("Bad data pre-warning: St.John's Church of England School Stanmore is corrupt, so the address is lost. You'll need to fix this manually.", log.WARNING)
		elif "special" in response.url:
			age_range = "special"
		elif "college" in response.url:
			age_range = "college"
			self.log("Bad data pre-warning: Harrow College is corrupt, so the address is a bit broken. You'll need to fix this manually.", log.WARNING)
		else:
			self.log("Unexpected url - couldn't find age range, skipping. URL: {}".format(response.url), log.ERROR)
			return []

		school = School()
		schools = []
		address = []
		for div in divs:
			if div.select('@class').extract()[0] == 'spacer':
				# finished previous school
				# the final school does have a spacer after it
				school.set_addr(address)
				school['age_range'] = age_range
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
						if label not in self.ignore:
							self.log("Discarding '{}' as not found in mapping".format(label), level=log.WARNING)

		return schools
