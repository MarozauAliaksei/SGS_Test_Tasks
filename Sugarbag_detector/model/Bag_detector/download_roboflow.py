from roboflow import Roboflow

rf = Roboflow(api_key="zZRfohUdBMc9kojyA7CD")
project = rf.workspace("aliakseiworkspace").project("test_task_1-7weyz")
version = project.version(4)
dataset = version.download("yolov11")