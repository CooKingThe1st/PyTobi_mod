from textGrid import TextGrid, Tiers, Tier, Annotation
from math import sqrt

class TextGridOperations:

	def __init__(self, basepath):

		pathIn = basepath + "_sum4.TextGrid"

		pathOut = basepath + "_result.TextGrid"

		self.textGrid = TextGrid(pathIn)
		self.fricatives = self.loadDictionaries("dict/fricatives.txt")
		self.unvoiced = self.loadDictionaries("dict/unvoiced.txt")
		# need to change, dis dict is diff for another lang
		self.xmin = self.textGrid.tiers.xmin
		self.xmax = self.textGrid.tiers.xmax
		self.computeZscores()
		self.createTonesBreaks(basepath)
		self.write2Txg(pathOut)

	def loadDictionaries(self, path):
		dictlist = []
		fd = open(path,"r")
		lines = fd.readlines()
		for line in lines:
			dictlist.append(line.strip())

		return dictlist

	# matched with fricative (bee zapping) and unvoiced (k and t at end)
	def matchDict(self, phone):
		match = False
		if phone in self.fricatives or phone in self.unvoiced:
			match = True

		return match

	# cal z score with mean phone and add feature to word
	def computeZscores(self):
		words = self.getAnnotations("words", self.xmin, self.xmax)
		tot = len(words) 

		for w in words:
			word_s = w.xmin
			word_e = w.xmax
			if w.head:
				# AVG phone per ms
				mean = self.z_scorePhone(word_s, word_e)
				w = self.z_scoreIp(w, mean)

	def z_scorePhone(self, start, end):
		phones = self.getAnnotations("phones", start, end)
		# get all phones according to word
		mean = (end - start)/ len(phones)
		if len(phones) > 2:
			dur_pho = []
			sqr_p = 0
			dev = 0
			for i,p in enumerate(phones):
				head = p.head
				dur_p = p.xmax - p.xmin
				dur_pho.append(dur_p)
				sqr_add = (dur_p - mean)**2
				sqr_p = sqr_p + sqr_add

			if sqr_p != 0:
				cal = sqr_p / len(phones)
				dev = sqrt(cal)
			if dev != 0 and mean != 0:
				for d in dur_pho:
					z_p = (d - mean) / dev
					# ambiguous here, what is p
					p.addFeature("z_dur", z_p)

		return mean

	# add new feature z_dur to original word annotate, with mean calculated 
	def z_scoreIp(self, word, mean):
		iP = self.getAnnotations("IP", self.xmin, self.xmax)

		ip_start = 0
		ip_end = 0
		for p in iP:
			if word.xmax > p.xmin and (word.xmax < p.xmax or word.xmax == p.xmax) and p.text.features:
				ip_start = p.xmin
				ip_end = p.xmax

		z_dur = 0
		if ip_end != 0:
			ref_ip = self.getAnnotations("IP", ip_start, ip_end)[0]
			ip_mean = ref_ip.text.getFeature("phone_mean")
			ip_std = ref_ip.text.getFeature("phone_std")
			z_dur = (mean - float(ip_mean))/ float(ip_std)
			word.addFeature("z_dur", z_dur)

		return word

	def featuresToFloat(self,feature):
		if feature != "--undefined--" and feature:
			feature = float(feature) 
		elif feature == "--undefined--":
			feature = None

		return feature

	# main changes here, get all phone inside words then append break, output to text
	def createTonesBreaks(self, basepath):

		customBreakPathOut = basepath + "_modBreak.txt"
		originalBreakPathOut = basepath + "_orgBreak.txt"
		originalTonePathOut = basepath + "_orgTone.txt"

		toneTier = self.createTier("tones", self.xmin, self.xmax, "point")
		breakTier = self.createTier("breaks", self.xmin, self.xmax, "point")
		
		words = self.getAnnotations("words", self.xmin, self.xmax)

		modPhoneBreak = ""
		orgPhoneBreak = ""
		orgPhoneTone = ""

		prev_f = 0
		prev_i = 0
		prev_d = 0
		for n,w in enumerate(words):
			word_s = w.xmin
			word_e = w.xmax
			head = w.head

			# get all phone from word
			if head:
				modPhoneBreak = modPhoneBreak + "{ "
				orgPhoneBreak = orgPhoneBreak + " "
				orgPhoneTone = orgPhoneTone + " "

				phones = self.getAnnotations("phones", word_s, word_e)
				for p in phones:
					modPhoneBreak = modPhoneBreak + p.head + ' '
				orgPhoneBreak = orgPhoneBreak + head + " "
				orgPhoneTone = orgPhoneTone + head + " "
			br = None

			curr_f0 = self.featuresToFloat(w.text.getFeature("z_f0"))
			curr_int = self.featuresToFloat(w.text.getFeature("z_int"))
			z_dur = self.featuresToFloat(w.text.getFeature("z_dur"))

			# ToneTier create here, not consider relation bw phone (not use), but actual z and f0
			# COULD MODIFY HERE ACCORDING TO LANG, dis is but a suggestion of original author
			curr_ave = 0 
			if z_dur and curr_f0 and curr_int:
				if head:
					curr_ave = (curr_f0 + curr_int + z_dur)/3
					w.addFeature("promScore", curr_ave)
				if n != 1:
					if curr_f0 > prev_f and curr_f0 > 0.1:
						point, tobilab = self.createPromPoints(w)
						prom = self.createAnnotation(point, point, tobilab)
						prom.head = tobilab
						prom.text.head = tobilab
						self.addAnnotationToTier(toneTier, prom)
						orgPhoneTone = orgPhoneTone + tobilab
					elif curr_f0 <= prev_f and curr_f0 > 0.1:
						point, tobilab = self.createPromPoints(w)
						prom = self.createAnnotation(point, point, tobilab)
						prom.head = tobilab
						prom.text.head = tobilab
						self.addAnnotationToTier(toneTier, prom)
						orgPhoneTone = orgPhoneTone + tobilab
					# Secondary prominence detection (based on intensity and duration)
					elif curr_int > prev_i and z_dur > prev_d and curr_ave > 0.1:
						point, tobilab = self.createPromPoints(w)
						prom = self.createAnnotation(point, point)
						prom.head = tobilab
						prom.text.head = tobilab						
						self.addAnnotationToTier(toneTier, prom)
						orgPhoneTone = orgPhoneTone + tobilab
					elif curr_int > prev_i and curr_ave > 0.1:
						point, tobilab = self.createPromPoints(w)
						prom = self.createAnnotation(point, point)
						prom.head = tobilab
						prom.text.head = tobilab
						self.addAnnotationToTier(toneTier, prom)
						orgPhoneTone = orgPhoneTone + tobilab
					elif prev_d > z_dur and prev_d > 0.1:
						point, tobilab = self.createPromPoints(w)
						prom = self.createAnnotation(point, point)
						prom.head = tobilab
						prom.text.head = tobilab
						self.addAnnotationToTier(toneTier, prom)
						orgPhoneTone = orgPhoneTone + tobilab
				
				prev_f = curr_f0
				prev_i = curr_int
				prev_d = z_dur

			# BREAK ANNOTATE
			if head: # if is word

				br = self.computeBreakFeat(word_e)
				breakP = self.createAnnotation(word_e, word_e)
				breakP.head = br
				breakP.text.head = br
				self.addAnnotationToTier(breakTier, breakP)

				modPhoneBreak = modPhoneBreak + "BRK" + str(br) + " }"
				orgPhoneBreak = orgPhoneBreak + "BRK" + str(br) + " "
 
				# if end phrase add another tone
				if br == 3 or br == 4:
					bt = self.tobiAnotation(w, br)
					tobibt = self.createAnnotation(word_e, word_e)
					tobibt.head = bt
					tobibt.text.head = bt
					self.addAnnotationToTier(toneTier, tobibt)
					orgPhoneTone = orgPhoneTone + " " + bt

		self.addTier("tones", toneTier)
		self.addTier("breaks", breakTier)

		# print("Tones and breaks have been annotated")
		# print("....................................")
		# print("PRINTING CUSTOM OUTPUT")
		# print("....................................")
		mod_result = open(customBreakPathOut, "w")
		mod_result.write(modPhoneBreak)
		mod_result.close()

		mod_result = open(originalBreakPathOut, "w")
		mod_result.write(orgPhoneBreak)
		mod_result.close()

		mod_result = open(originalTonePathOut, "w")
		mod_result.write(orgPhoneTone)
		mod_result.close()
		# print("DONE")

	# prominent time for tone
	def createPromPoints(self,word):
		word_s = word.xmin
		word_e = word.xmax
		point = 0
		if word.head:
			#print(w.head)
			ph_inw = self.getAnnotations("phones", word_s, word_e)
			for idp,p in enumerate(ph_inw):
				phone = p.head
				if phone and phone[-1] == "1":
					point = ((p.xmax - p.xmin)/2) + p.xmin
				# Check if needed for breaks
				if phone and idp == len(ph_inw):
					point = ((p.xmax - p.xmin)/2) + p.xmin
					
		tobilab = self.tobiAnotation(word)

		return point, tobilab

	# calculate tones
	def tobiAnotation(self, word, idx= None):
		f0 = self.featuresToFloat(word.text.getFeature("z_f0"))
		slope = self.featuresToFloat(word.text.getFeature("slope"))
		range_f = self.featuresToFloat(word.text.getFeature("rangeF0"))
		n_phone = self.featuresToFloat(word.text.getFeature("n_Phones"))

		tobi = ""
		if not idx and slope and f0 and slope < 20 and slope > -20 and f0 > 1:
			tobi = "H*" 
		elif slope and range_f and slope > 20 and range_f > 40 :
			if idx == 4:
				tobi = "L-H%"
			elif idx == 3:
				tobi = "LH-"
			elif idx == None and n_phone > 4:
				tobi = "L*+H"
			elif idx == None and n_phone < 4:
				tobi = "L+H*"
		elif slope and range_f and slope < -20 and range_f > 40:
			if idx == 4:
				tobi = "H-L%"
			elif idx == 3:
				tobi = "HL-"
			elif idx == None:
				tobi = "H*+L"
		elif f0 and f0 > 0.9 and idx == None:
			tobi = "H*"
		elif f0 and f0 > 0.5 and idx == None:
			tobi = "!H*"
		else:
			if idx == 4:
				tobi = "L-L%"
			if idx == 3:
				tobi = "LL-"
			elif idx == None:
				tobi = "L*"

		return tobi

	# calculate break
	def computeBreakFeat(self, time):
		words = self.getAnnotations("words", self.xmin, self.xmax)
		br = None
		# iter to get index of next word
		# only use diff in time to check break, SHOULD BE CHANGED 
		for word in words:
			if word.xmin == time:
				dur = word.xmax - word.xmin
				if word.head == None and dur >= 0.2 and dur < 0.6:
					br = 4
				elif word.head == None and dur < 0.2:
					br = 3
				elif word.head == None and dur >= 0.6:
					br = 5

		if br == None:
			next_pho = None
			last_phodur = 0
			last_pho = None
			for word in words:
				# find last phone
				if word.xmax == time:
					# get numphones of word from text_grid mod4, which based on MFA, buf do it have prediction ?
					n_phones = int(word.text.getFeature("n_Phones"))
					if n_phones > 4:
						phones = self.getAnnotations("phones", word.xmin, word.xmax)
						# get the last phone only if long word
						for p in phones:
							if p.xmax == word.xmax:
								last_pho = p.head
								last_phodur = p.xmax - p.xmin
				# find next phone
				elif word.xmin == time:
					phones = self.getAnnotations("phones", word.xmin, word.xmax)
					for p in phones:
						if p.xmin == word.xmin:
							next_pho = p.head
			if br == None and next_pho and last_pho:
				match1 = self.matchDict(last_pho)
				match2 = self.matchDict(next_pho)
				if match1 or match2:
					br = 2
				else:
					br = 1
			else:
				br = 1

		return br

	def write2Txg(self, path):
		self.textGrid.writeTextGrid(path)

	def createAnnotation(self, xmin, xmax, head=None, features=None):
		iAnn = Annotation(xmin, xmax, features=features, head=head)
		return iAnn

	def createTier(self, name, xmin, xmax, tierType=None):
		iTier = Tier(name, xmin, xmax, tierType)
		return iTier

	def addFeatureToAnnotation(self, ann, key, value):
		ann.addFeature(key, value)

	def addAnnotationToTier(self, tier, ann):
		tier.addAnnotation(ann)

	def addTier(self, tierName, tier):
		self.textGrid.tiers.addTier(tierName, tier)

	def getAnnotations(self, tier, start, end):
		return self.textGrid.getAnnotations(tier, start, end)

	def getFeatureFromAnnotation(self, ann, featureName):
		return ann.getFeature(featureName)

if __name__ == '__main__':
	import sys
	path = sys.argv[1]
	filename = sys.argv[2]

	iT = TextGridOperations(path+filename)
