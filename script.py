##  QGIS-open-url-action-script 
##  Copyright (C) 2018  Clément Ronzon
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import Qt, QUrl, QSettings
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView, QWebPage
import sys

class MyBrowser(QWebView):
	def __init__(self, html = ''):
		super(MyBrowser, self).__init__()
		self.stop()
		self.loadFinished.connect(self.handleLoadFinished)
		self.loadProgress.connect(self.handleLoadProgress)
		self.html = html

	def handleLoadProgress(self, percent):
		qPrint('Loading: ' + str(percent) + '%')

	def handleLoadFinished(self):
		qPrint('Load Finished')
		self.insertHtml()

	def insertHtml(self):
		self.page().mainFrame().findFirstElement('header').appendInside(self.html)

class MySelection(QgsMapTool):
	def __init__(self, canvas, layer, x, y):
		QgsMapTool.__init__(self, canvas)
		self.canvas = canvas
		self.layer = layer
		self.x = x
		self.y = y

	def getFeatureRequest(self):
		sr = self.searchRadiusMU(self.canvas)
		r = QgsRectangle()
		r.setXMinimum(x - sr)
		r.setXMaximum(x + sr)
		r.setYMinimum(y - sr)
		r.setYMaximum(y + sr)
		r = self.toLayerCoordinates(self.layer, r)
		return QgsFeatureRequest().setFilterRect(r).setFlags(QgsFeatureRequest.ExactIntersect)

	def getFeaures(self):
		return self.layer.getFeatures(self.getFeatureRequest())

	def getLastFeature(self):
		feature = QgsFeature()
		features = self.layer.getFeatures(self.getFeatureRequest())
		for feature in features:
			pass
		return feature

	def getLastFeatureId(self):
		return self.getLastFeature().id()

class MyFormatter:
	def __init__(self, fieldNames, attrPattern = '<li><span>%s:</span> %s</li>', wrapperPattern = '<ul>%s</ul>'):
		self.fieldNames = fieldNames
		self.attrPattern = attrPattern
		self.wrapperPattern = wrapperPattern

	def formatAttributes(self, attributes):
		attrList = []
		i = 0
		for attrVal in attributes:
			name = self.fieldNames[i]
			attrStrVal = ''
			try:
				attrStrVal = unicode(attrVal).encode('ascii', 'ignore')
			except (UnicodeEncodeError, UnicodeDecodeError):
				attrStrVal = '#err#'
				qPrint('UnicodeEncodeError')
			attrList.append(self.attrPattern % (name, attrStrVal))
			i += 1
		return self.wrapperPattern % ''.join(attr for attr in attrList)

class MyLayerHelper:
	def __init__(self, layer):
		self.layer = layer

	def getFieldNames(self):
		return list(map(lambda field: field.displayName(), self.layer.fields()))

	def getFeature(self, id):
		feature = QgsFeature()
		features = self.layer.getFeatures(QgsFeatureRequest(id))
		features.nextFeature(feature)
		return feature

	def getFeatureAttributes(self, id):
		return self.getFeature(id).attributes()

class MyContext:
	def __init__(self, iface):
		self.iface = iface

	def getLayer(self):
		return self.iface.activeLayer()

	def getCanvas(self):
		return self.iface.mapCanvas()

def qPrint(message):
	txt = unicode(message)
	if txt:
		QgsMessageLog.logMessage(txt, tag="pics", level=QgsMessageLog.INFO)
		

if __name__=='__main__':
	currentId = [% $id %]
	x = [%$clickx%]
	y = [%$clicky%]
	url = '[% url %]'
	QApplication.setOverrideCursor(Qt.WaitCursor)
	qPrint('---------')
	qPrint('Python version: ' + sys.version)
	context = MyContext(qgis.utils.iface)
	layer = context.getLayer()
	selection = MySelection(context.getCanvas(), layer, x, y)
	if selection.getLastFeatureId() == currentId:
		qPrint('Opening url: ' + url)
		layer.selectByIds([currentId])
		helper = MyLayerHelper(layer)
		featureAttrs = helper.getFeatureAttributes(currentId)
		formatter = MyFormatter(helper.getFieldNames())
		html = '<div>%s</div>' % formatter.formatAttributes(featureAttrs)
		browser = MyBrowser(html)
		browser.load(QUrl(url))
		browser.show()
	else:
		qPrint('Stacked features, ignoring feature ' + str(currentId))
	QApplication.restoreOverrideCursor()