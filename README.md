# QGIS open url action script
This Python action script allows to open a url in the embedded browser and visualise the feature's attributes at the same time.

To use it:

  - make sure that your layer has an attribute named `url` with proper urls in it
  - make sure that the current CRS is EPSG:4326
  - open the layer's properties window
  - click on the actions tab
  - add a Python script, copy and paste the code from this repository
  - click ok twice
  - use the `actions` button in the toolbar then click on any feature
