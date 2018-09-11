CD %~dp0
FOR %%A IN (%*) DO (
	SET USEFILE=%%A
	java -jar ../jar/processing-py.jar gcode_image_maker.pyde
	)
pause 

REM Now your batch file handles %%A instead of %1
REM processing-java --sketch=gcode_image_maker.pyde --run argu %%A
REM processing-py --sketch=gcode_image_maker.pyde --run argu jab4c20case_1.gcode

REM https://stackoverflow.com/questions/16302351/ms-dos-batch-file-pause-with-enter-key

REM https://stackoverflow.com/questions/14786623/batch-file-copy-using-1-for-drag-and-drop
REM https://stackoverflow.com/questions/44577446/open-file-by-dragging-and-dropping-it-onto-batch-file?rq=1

REM https://stackoverflow.com/questions/1243240/drag-and-drop-batch-file-for-multiple-files

REM https://forum.processing.org/two/discussion/23924/handling-command-line-arguments-in-a-sketch

REM https://py.processing.org/tutorials/command-line/

REM https://stackoverflow.com/questions/17063947/get-current-batchfile-directory