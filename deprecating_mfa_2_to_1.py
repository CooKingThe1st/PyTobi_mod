from textGrid import TextGrid, Tiers, Tier, Annotation
from math import sqrt
from copy import deepcopy

class TextGridOperations:

	def __init__(self, basepath):

		pathIn = basepath + ".TextGrid"

		pathOut = basepath + "_adapt.TextGrid"
		
		phOut = basepath + ".ph"

		self.textGrid = TextGrid(pathIn)
		# need to change, dis dict is diff for another lang
		# modify directly to textGrid
		self.xmin = self.textGrid.tiers.xmin
		self.xmax = self.textGrid.tiers.xmax
		# self.computeZscores()
		# self.createTonesBreaks(basepath)
		self.adaptVerTwo(pathOut, phOut)

#WARNING HAVE CHANGE TEXTGRID CODE TO ADAPT, IF NEED TO GEN TEXTGRID2.0 PLEASE REDO the TIERS LIST OUTPUT in TEXTGRID
	def adaptVerTwo(self, pathOut, phOut):
		# print(self.textGrid.tiers)
		phone = deepcopy(self.textGrid.tiers.getTier("phones"))
		word = deepcopy(phone)
		word.name = "words"
		# print(word.xmin, word.xmax, word.name)
		# print(word.getAnnotations(0, word.xmax))
		# print(new_tiers.getAllTiers()[0])
		# print(self.textGrid.getOutputAnnotations(new_tiers.getAllTiers()[0]))
		phones = phone.getAnnotations(self.xmin, self.xmax)
		
		phTxtOut = ""
		
		for n,w in enumerate(phones):
			if not w.head:
				# new_ann = self.createAnnotation(w.xmin, w.xmax)
				# new_ann.head = "sp"
				# new_ann.text.head = "sp"
				# w = new_ann
				w.head = "sp"
				w.text.head = "sp"
			else:
				w.head = w.head.replace("ː", "*").replace("˨ˀ˥","ʮ").replace("˨ˀ˦","ʯ")
				w.text.head = w.text.head.replace("ː", "*").replace("˨ˀ˥","ʮ").replace("˨ˀ˦","ʯ")

		words = word.getAnnotations(self.xmin, self.xmax)
		for n,w in enumerate(words):
			if w.head:
				w.head = w.head.replace("ː", "*").replace("˨ˀ˥","ʮ").replace("˨ˀ˦","ʯ")
				w.text.head = w.text.head.replace("ː", "*").replace("˨ˀ˥","ʮ").replace("˨ˀ˦","ʯ")
				phTxtOut = phTxtOut + w.head + " "
			else:
				if not(n == 0) and not(n == len(phones) - 1) and not(n == len(words)-1):
					w.head = "sep"
					w.text.head = "sep"
					
					phTxtOut = phTxtOut + "| "

		new_tiers = Tiers(self.xmin, self.xmax)
		new_tiers.addTier("words", word)
		new_tiers.addTier("phones", phone)
		self.textGrid.tiers = new_tiers
		self.textGrid.writeTextGrid(pathOut)
		
		with open(phOut, 'w') as phfile:
			phfile.write(phTxtOut)

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
